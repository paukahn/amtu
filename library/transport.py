"""Capa de transporte async para la SP-API.

Una sola corrutina `request()` concentra: espera del rate limiter, envío con
`httpx.AsyncClient`, actualización del limiter desde las cabeceras, detección
de throttling (HTTP 429 y errores `QuotaExceeded`/`TooManyRequests` en el
cuerpo), señalización de 401 y timeout por defecto. El reintento se hace con
tenacity (async).

Política de reintentos (pase 2 — antes solo se reintentaba el throttling):
- AmazonThrottleError (429 / quota en el cuerpo)
- AmazonServerError (HTTP 5xx, transitorios habituales en la SP-API)
- httpx.TransportError (fallos de red: conexión, timeout, lectura)

Nota sobre idempotencia: también se reintentan POST. Para esta aplicación es
aceptable: un createReport duplicado deja un reporte huérfano inocuo y los
feeds (stock PATCH absoluto, confirmación de envíos) son re-aplicables. Si se
añade un endpoint donde un duplicado haga daño, hay que excluirlo aquí.

- 401 -> AmazonAuthError (NO se reintenta aquí): el cliente que posee el
  token_provider decide refrescar y reintentar.
- timeout por defecto SIEMPRE.
- la estrategia de espera del retry es inyectable para poder testear sin
  dormir segundos reales.
- el log de debug redacta el token y no llama a `.json()` a ciegas.
"""

from __future__ import annotations

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_random,
)

from library.exceptions import AmazonThrottleError, AmazonServerError, AmazonAuthError

import re

# Campos sensibles que pueden aparecer en los cuerpos de respuesta de la SP-API
# y que NO deben quedar en claro en el log de debug: el RestrictedDataToken y
# las URL pre-firmadas de S3 (dan acceso directo al documento, a menudo con PII).
_REDACT_BODY_FIELDS = ("restrictedDataToken", "url")
_REDACT_BODY_RE = re.compile(
    r'("(?:' + "|".join(_REDACT_BODY_FIELDS) + r')"\s*:\s*")(.*?)(")',
    re.DOTALL,
)


def _redact_body(text: str) -> str:
    return _REDACT_BODY_RE.sub(r"\1***\3", text)

# (timeout total, connect). Conservador pero acotado: nunca colgar indefinidamente.
DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)

_THROTTLE_CODES = ("QuotaExceeded", "TooManyRequests")
_REDACT_HEADERS = ("x-amz-access-token", "authorization")
_RETRYABLE = (AmazonThrottleError, AmazonServerError, httpx.TransportError)


class AsyncTransport:
    def __init__(
        self,
        client: httpx.AsyncClient,
        limiter,
        *,
        debug: bool = False,
        throttle_attempts: int = 5,
        throttle_wait=None,
    ):
        self._client = client
        self._limiter = limiter
        self._debug = debug
        self._throttle_attempts = throttle_attempts
        # Espera por defecto del reintento (exponencial 5..60s) + jitter para
        # evitar sincronización entre corrutinas.
        base_wait = throttle_wait or (
            wait_exponential(multiplier=1, min=5, max=60) + wait_random(0, 1)
        )

        # Pase 3: si el 429 trajo Retry-After, respetarlo — la exponencial por
        # sí sola podía agotar los 5 intentos dentro de la misma ventana de
        # cuota cerrada (createFeed: 1 req / 2 min).
        def _wait_respecting_retry_after(retry_state):
            delay = base_wait(retry_state)
            outcome = retry_state.outcome
            if outcome is not None and outcome.failed:
                retry_after = getattr(outcome.exception(), "retry_after", None)
                if retry_after:
                    delay = max(delay, retry_after)
            return delay

        self._throttle_wait = _wait_respecting_retry_after

    async def request(
        self,
        method: str,
        url: str,
        *,
        market: str,
        endpoint_key: str,
        **kwargs,
    ) -> httpx.Response:
        async for attempt in AsyncRetrying(
            wait=self._throttle_wait,
            stop=stop_after_attempt(self._throttle_attempts),
            retry=retry_if_exception_type(_RETRYABLE),
            reraise=True,
        ):
            with attempt:
                return await self._do_request(method, url, market, endpoint_key, **kwargs)

    async def _do_request(self, method, url, market, endpoint_key, **kwargs) -> httpx.Response:
        await self._limiter.wait(market, endpoint_key)
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        response = await self._client.request(method, url, **kwargs)
        self._limiter.update(market, endpoint_key, response.headers)

        if self._debug:
            self._log_debug(response)

        # x-amzn-RequestId (pase 3f): identificador que pide Amazon Developer
        # Support para investigar cualquier caso — sin él, escalar un fallo
        # como 'InvalidInput' sin detalle es prácticamente imposible.
        request_id = response.headers.get("x-amzn-RequestId")

        if response.status_code == 429:
            err = AmazonThrottleError(
                f"HTTP 429: {response.text}", status_code=429, body=response.text, request_id=request_id
            )
            try:
                retry_after = response.headers.get("Retry-After")
                err.retry_after = float(retry_after) if retry_after else None
            except (TypeError, ValueError):
                err.retry_after = None
            raise err
        if response.status_code == 401:
            raise AmazonAuthError(
                f"HTTP 401: {response.text}", status_code=401, body=response.text, request_id=request_id
            )
        if response.status_code >= 500:
            raise AmazonServerError(
                f"HTTP {response.status_code}: {response.text}",
                status_code=response.status_code,
                body=response.text,
                request_id=request_id,
            )

        # QuotaExceeded/TooManyRequests pueden venir en el cuerpo con 200/4xx.
        ctype = response.headers.get("content-type", "")
        if "json" in ctype and response.content:
            try:
                data = response.json()
            except ValueError:
                data = None
            if isinstance(data, dict) and data.get("errors"):
                codes = [e.get("code") for e in data["errors"] if isinstance(e, dict)]
                if any(c in _THROTTLE_CODES for c in codes):
                    raise AmazonThrottleError(
                        f"QuotaExceeded: {data['errors']}",
                        status_code=response.status_code,
                        body=response.text,
                        request_id=request_id,
                    )

        return response

    def _log_debug(self, response: httpx.Response) -> None:
        from library.logging_helpers import debug

        req = response.request
        redacted = {
            k: ("***" if k.lower() in _REDACT_HEADERS else v)
            for k, v in req.headers.items()
        }
        debug(f"{req.method} {req.url} -> {response.status_code}")
        debug(f"req headers: {redacted}")
        # Redactar el cuerpo: contiene restrictedDataToken y URL pre-firmadas de
        # S3. Antes se logueaba dócil body[:1000] dejando esos secretos en disco.
        body = _redact_body(response.text)
        debug(f"resp body: {body[:1000]}{'…' if len(body) > 1000 else ''}")
