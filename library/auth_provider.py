"""Proveedor de tokens async para LWA (Login With Amazon).

Mismo papel que en el pase 1 (credenciales de ApplicationsConfig / TokensConfig
/ AccountsConfig, caché en disco `cache/<account>/access_token_<market>`, lock
por mercado, `force_refresh` para el retry-on-401 del cliente), con dos
mejoras de fiabilidad:

- La validez del token usa el `expires_in` REAL de la respuesta LWA (con un
  margen de seguridad), no la heurística de mtime de 50 minutos. El fichero de
  caché pasa a ser JSON {"access_token", "expires_at"}; un fichero antiguo en
  texto plano se trata como caducado y se refresca una vez.
- El refresh LWA se reintenta con tenacity ante fallos de red y 5xx (antes un
  parpadeo de red durante el refresh tiraba la cuenta entera del lote).
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import timedelta

import httpx
from tenacity import AsyncRetrying, retry_if_exception, stop_after_attempt, wait_exponential

from classes.config import AccountsConfig, ApplicationsConfig
from classes.config.Token import TokensConfig

LWA_URL = "https://api.amazon.com/auth/o2/token"
DEFAULT_TTL = timedelta(minutes=50)  # fallback si LWA no devolviera expires_in
SAFETY_MARGIN = 60.0  # segundos antes de la caducidad real en los que ya refrescamos
_REFRESH_ATTEMPTS = 3


def _is_transient_lwa_error(exc: BaseException) -> bool:
    if isinstance(exc, httpx.TransportError):
        return True
    return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code >= 500


def _read_cache(path: str, key=None, hmac_key=None):
    """Devuelve (token, expires_at).

    Con key/hmac_key el fichero se descifra (AES+HMAC, data_protector). Un
    fichero ilegible/descifrado-fallido o de un formato anterior (texto plano)
    se trata como CADUCADO (None, 0.0) para forzar un refresh que lo regenere
    cifrado — así migra solo desde el formato plaintext antiguo.
    """
    if not os.path.exists(path):
        return None, 0.0
    try:
        if key and hmac_key:
            from library.security.data_protector import decrypt
            raw = decrypt(path, key, hmac_key)
        else:
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
        raw = raw.strip()
    except Exception:
        # MAC inválido, fichero plaintext legado leído con llaves, I/O, etc.
        return None, 0.0
    if not raw:
        return None, 0.0
    try:
        data = json.loads(raw)
        return data["access_token"], float(data["expires_at"])
    except (ValueError, KeyError, TypeError):
        return None, 0.0


def _write_cache(path: str, token: str, expires_at: float, key=None, hmac_key=None) -> None:
    # Escritura atómica (temp + os.replace): evita lecturas a medias entre
    # procesos. Con key/hmac_key el contenido se cifra en reposo (el access
    # token es un bearer vivo; ya teníamos las llaves a mano).
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = json.dumps({"access_token": token, "expires_at": expires_at}).encode("utf-8")
    if key and hmac_key:
        from library.security.data_protector import encrypt
        blob = encrypt(payload, key, hmac_key)
    else:
        blob = payload
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "wb") as f:
        f.write(blob)
    os.replace(tmp, path)


def _still_valid(expires_at: float, now: float | None = None) -> bool:
    return (now if now is not None else time.time()) < (expires_at - SAFETY_MARGIN)


class AsyncTokenProvider:
    def __init__(
        self,
        application_name: str,
        account: str,
        http_client: httpx.AsyncClient,
        *,
        key=None,
        hmac_key=None,
        lwa_url: str = LWA_URL,
        ttl: timedelta = DEFAULT_TTL,
    ):
        self._http = http_client
        self.application_name = application_name
        self.account = account
        self._lwa_url = lwa_url
        self._ttl = ttl
        self._key = key
        self._hmac_key = hmac_key

        apps = ApplicationsConfig(key=key, hmac_key=hmac_key)
        self.client_id = apps.get_client_id(application_name)
        self.client_secret = apps.get_client_secret(application_name)
        if not self.client_id or not self.client_secret:
            raise ValueError(f"Credenciales no encontradas para la aplicación '{application_name}'.")

        accounts = AccountsConfig("config").get_all_accounts()
        if account not in accounts:
            raise ValueError(f"Cuenta '{account}' no encontrada en cuentas.")
        if accounts[account].get("aplicacion") != application_name:
            raise ValueError(f"La cuenta '{account}' no está vinculada a la aplicación '{application_name}'.")
        self.markets = accounts[account].get("mercados", [])

        acc_tokens = TokensConfig(key=key, hmac_key=hmac_key).get_account_tokens(account)
        self._refresh_tokens = {m: acc_tokens.get(f"refresh_token_{m}") for m in self.markets}
        self._access: dict[str, tuple[str, float]] = {}  # market -> (token, expires_at)
        self._locks: dict[str, asyncio.Lock] = {}

    def _cache_path(self, market: str) -> str:
        return os.path.join("cache", self.account, f"access_token_{market}")

    def _lock(self, market: str) -> asyncio.Lock:
        if market not in self._locks:
            self._locks[market] = asyncio.Lock()
        return self._locks[market]

    def _valid_token(self, market: str) -> str | None:
        token, expires_at = self._access.get(market, (None, 0.0))
        if token and _still_valid(expires_at):
            return token
        token, expires_at = _read_cache(self._cache_path(market), self._key, self._hmac_key)
        if token and _still_valid(expires_at):
            self._access[market] = (token, expires_at)
            return token
        return None

    async def get_access_token(self, market: str, force_refresh: bool = False) -> str:
        if market not in self._refresh_tokens:
            raise ValueError(f"Mercado '{market}' no configurado para la cuenta '{self.account}'")

        if not force_refresh:
            token = self._valid_token(market)
            if token:
                return token

        # Token que íbamos a reemplazar (el que recibió el 401 en el caso
        # force_refresh). Si otra corrutina lo refresca mientras esperamos el
        # lock, lo detectamos abajo y evitamos un POST a LWA redundante.
        stale = self._access.get(market, (None, 0.0))[0]

        async with self._lock(market):
            # Re-chequear SIEMPRE (también con force_refresh): otra corrutina
            # pudo refrescar mientras esperábamos el lock. Antes este re-check
            # se saltaba con force_refresh=True, así que N peticiones del mismo
            # mercado con 401 simultáneo disparaban N refrescos LWA en serie.
            token = self._valid_token(market)
            if token and (not force_refresh or token != stale):
                return token
            return await self._refresh(market)

    async def _refresh(self, market: str) -> str:
        refresh_token = self._refresh_tokens.get(market)
        if not refresh_token:
            raise ValueError(f"No hay refresh token para {market} en cuenta '{self.account}'")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        resp = None
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(_REFRESH_ATTEMPTS),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception(_is_transient_lwa_error),
            reraise=True,
        ):
            with attempt:
                resp = await self._http.post(
                    self._lwa_url, data=data, timeout=httpx.Timeout(15.0, connect=10.0)
                )
                resp.raise_for_status()

        payload = resp.json()
        token = payload.get("access_token")
        if not token:
            raise ValueError(f"No se recibió access token para {market}")

        expires_in = payload.get("expires_in") or self._ttl.total_seconds()
        expires_at = time.time() + float(expires_in)

        self._access[market] = (token, expires_at)
        _write_cache(self._cache_path(market), token, expires_at, self._key, self._hmac_key)
        return token
