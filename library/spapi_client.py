"""Fachada async de la SP-API: agrupa Reports / Feeds / Tokens.

`AmazonClient` mantiene el estado (market + transporte + proveedor de tokens +
config de polling) y expone métodos de alto nivel que devuelven modelos
Pydantic.

Novedades del pase 2:
- `run_report()` encapsula la cadena create -> poll -> (RDT) -> download que
  orders / vat reescribían a mano cada uno.
- `download_report_content` respeta `compressionAlgorithm` del documento:
  los reportes comprimidos (p.ej. GET_VAT_TRANSACTION_DATA) se descomprimen
  aquí; antes cada módulo tenía que saber si su reporte venía en gzip.
- `create_report` ya no inventa fechas ("mes anterior") cuando no se pasan:
  esa política era de los módulos y vive ahora en vat_report. Sin fechas, el
  body no lleva dataStartTime/dataEndTime.
- `get_product_type` eliminado: no tenía llamadores desde que se quitó
  `enrich_feed_with_product_types`.

Mantiene: ante un 401, `_call` refresca el token y reintenta una vez; el
backoff del polling usa base_delay/factor/max_delay/jitter de PollingConfig.

Pase 3:
- `_call` valida el estado HTTP de TODAS las operaciones: un 400/403/404 se
  convierte en AmazonAPIError(status_code, body) con el cuerpo de error real
  de Amazon. Antes solo create_report comprobaba el estado y el resto acababa
  en un pydantic.ValidationError mudo que perdía el diagnóstico.
- Las operaciones S3 pre-firmadas (PUT/GET) se reintentan ante fallos de red
  y 5xx: un ReadTimeout en la descarga final ya no tira un reporte que Amazon
  ya generó (para VAT: un mes de datos y minutos de polling repetido).
- `download_feed_result_content` unifica la descarga+gunzip del resultado de
  un feed (stock y trackings tenían cada uno su copia del mismo bloque).
- `environment` ('production' | 'sandbox') selecciona el endpoint.
"""

from __future__ import annotations

import asyncio
import random

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential, wait_random

from library.marketplaces import get_market_endpoints
from library.transport import DEFAULT_TIMEOUT
from library.exceptions import (
    AmazonAPIError,
    AmazonAuthError,
    AmazonFeedNotReadyError,
    AmazonReportNotReadyError,
    AmazonServerError,
)
from library.models import (
    CreateFeedDocumentResponse,
    CreateFeedResponse,
    CreateReportResponse,
    FeedDocumentResponse,
    FeedStatusResponse,
    ReportDocumentResponse,
    ReportRun,
    ReportStatusResponse,
    RestrictedDataTokenResponse,
)

_TERMINAL = ("DONE", "CANCELLED", "FATAL")

# Reintento de operaciones S3 pre-firmadas: idempotentes por naturaleza
# (PUT del mismo contenido / GET), así que reintentar es seguro.
_S3_ATTEMPTS = 4
_S3_WAIT = wait_exponential(multiplier=1, min=2, max=30) + wait_random(0, 1)
_S3_RETRYABLE = (httpx.TransportError, AmazonServerError)


class AmazonClient:
    def __init__(self, market, transport, token_provider, polling_cfg, http_client, *,
                 environment="production"):
        self.market = market
        self._transport = transport
        self._tokens = token_provider
        self._polling = polling_cfg
        self._http = http_client
        self._endpoint = get_market_endpoints(market, environment)["endpoint"]

    # ── núcleo: token + 401-retry + validación de estado ───────────────────
    async def _call(self, method, url, endpoint_key, *, rdt_token=None, extra_headers=None, **kwargs) -> httpx.Response:
        refreshable = rdt_token is None
        access = rdt_token or await self._tokens.get_access_token(self.market)
        headers = dict(extra_headers or {})
        headers["x-amz-access-token"] = access
        try:
            resp = await self._transport.request(
                method, url, market=self.market, endpoint_key=endpoint_key, headers=headers, **kwargs
            )
        except AmazonAuthError:
            if not refreshable:
                raise
            access = await self._tokens.get_access_token(self.market, force_refresh=True)
            headers["x-amz-access-token"] = access
            resp = await self._transport.request(
                method, url, market=self.market, endpoint_key=endpoint_key, headers=headers, **kwargs
            )
        # El transporte ya convirtió 401/429/5xx en excepciones; aquí caen los
        # 4xx restantes (400/403/404…). SIN esto, model_validate(resp.json())
        # fallaba con un ValidationError que perdía el cuerpo {"errors": ...}
        # de Amazon — imposible diagnosticar por logs. El fallback de orders
        # sigue funcionando: recibe AmazonAPIError con status_code=400.
        if resp.status_code >= 400:
            request_id = resp.headers.get("x-amzn-RequestId")
            suffix = f" [x-amzn-RequestId: {request_id}]" if request_id else ""
            raise AmazonAPIError(
                f"HTTP {resp.status_code} en {endpoint_key}: {resp.text[:500]}{suffix}",
                status_code=resp.status_code,
                body=resp.text,
                request_id=request_id,
            )
        return resp

    async def _poll(self, section, exc_type, check):
        """Repite `check()` hasta que devuelva resultado (deja de lanzar exc_type),
        con backoff exponencial entre comprobaciones. Durante la espera escribe un
        «latido» cada pocos segundos para que NO parezca que el programa se colgó.
        Cualquier otra excepción (p. ej. throttling) se propaga, como antes."""
        from library.logging_helpers import info
        HEARTBEAT = 15.0
        base = self._polling.get_base_delay(section)
        factor = self._polling.get_factor(section)
        max_delay = self._polling.get_max_delay(section)
        jitter = self._polling.get_jitter(section)
        # max(1, ...): garantiza al menos un intento. Con max_attempts<=0 mal
        # configurado, range(1, attempts+1) sería vacío y _poll devolvería None
        # implícito -> AttributeError aguas abajo en run_report.
        attempts = max(1, int(self._polling.get_max_attempts(section)))
        delay = base
        for n in range(1, attempts + 1):
            try:
                return await check()
            except exc_type as e:
                if n >= attempts:
                    raise
                wait = min(delay, max_delay) + (random.uniform(0, jitter) if jitter else 0)
                info(f"⏳ Aún no está listo ({e}). Intento {n}/{attempts}; vuelvo a comprobar en ~{wait:.0f}s.")
                slept = 0.0
                while wait - slept > HEARTBEAT:
                    await asyncio.sleep(HEARTBEAT)
                    slept += HEARTBEAT
                    info(f"   … sigo esperando ({int(slept)}s de {int(wait)}s) …")
                await asyncio.sleep(max(0.0, wait - slept))
                delay *= factor

    # ── Reports ────────────────────────────────────────────────────────────
    async def create_report(self, shop, report_type, *, report_options=None, start_date=None, end_date=None) -> str:
        url = f"{self._endpoint}/reports/2021-06-30/reports"
        headers = {"accept": "application/json", "content-type": "application/json;charset=utf-8"}
        marketplace_ids = [shop] if isinstance(shop, str) else shop
        body = {
            "reportType": report_type,
            "marketplaceIds": marketplace_ids,
        }
        if start_date:
            body["dataStartTime"] = start_date
        if end_date:
            body["dataEndTime"] = end_date
        if report_options:
            body["reportOptions"] = report_options

        resp = await self._call("post", url, "POST /reports/2021-06-30/reports", extra_headers=headers, json=body)
        if resp.status_code != 202:
            # Nota: _call ya lanza AmazonAPIError para cualquier >=400 antes de
            # devolver; este chequeo solo queda como red de seguridad ante un
            # 2xx que no sea 202 (desviación de la spec, no observada nunca).
            raise AmazonAPIError(
                f"Error creando reporte {report_type}: {resp.status_code} - {resp.text}",
                status_code=resp.status_code,
                body=resp.text,
                request_id=resp.headers.get("x-amzn-RequestId"),
            )
        result = CreateReportResponse.model_validate(resp.json())
        from library.logging_helpers import info
        info(f"✅ [{report_type}] Creado ({self.market}) → {result.reportId}")
        return result.reportId

    async def get_report_status(self, report_id, section="reports") -> ReportStatusResponse:
        async def _check():
            url = f"{self._endpoint}/reports/2021-06-30/reports/{report_id}"
            headers = {"accept": "application/json", "content-type": "application/json;charset=utf-8"}
            resp = await self._call("get", url, "GET /reports/2021-06-30/reports/{id}", extra_headers=headers)
            result = ReportStatusResponse.model_validate(resp.json())
            if result.processingStatus not in _TERMINAL:
                raise AmazonReportNotReadyError(result.processingStatus)
            return result
        return await self._poll(section, AmazonReportNotReadyError, _check)

    async def get_report_document(self, report_document_id, *, rdt_token=None) -> ReportDocumentResponse:
        url = f"{self._endpoint}/reports/2021-06-30/documents/{report_document_id}"
        headers = {"accept": "application/json", "content-type": "application/json;charset=utf-8"}
        resp = await self._call("get", url, "GET /reports/2021-06-30/documents/{id}", rdt_token=rdt_token, extra_headers=headers)
        return ReportDocumentResponse.model_validate(resp.json())

    async def get_restricted_data_token(self, method, path, *, report_type=None) -> str:
        url = f"{self._endpoint}/tokens/2021-03-01/restrictedDataToken"
        headers = {"accept": "application/json", "content-type": "application/json;charset=utf-8"}
        resource = {"method": method, "path": path}
        # Comportamiento verificado en producción y conservado tal cual: para
        # rutas de documentos se envían dataElements/reportTypes aunque la spec
        # de Tokens 2021-03-01 no los documente para este path — Amazon los
        # tolera. (El antiguo кортеж PII_REQUIRED era código muerto: la única
        # llamada siempre pasa una ruta /documents/.) Cambiar esto exige
        # probarlo antes contra el sandbox con cada tipo de reporte.
        if "/documents/" in path:
            resource["dataElements"] = ["pII"]
        if report_type:
            resource["reportTypes"] = [report_type]
        resp = await self._call(
            "post", url, "POST /tokens/2021-03-01/restrictedDataToken",
            extra_headers=headers, json={"restrictedResources": [resource]},
        )
        return RestrictedDataTokenResponse.model_validate(resp.json()).restrictedDataToken

    async def download_report_content(self, report_doc_id, report_type) -> str:
        from library.helper_functions import gunzip_to_text

        resource_path = f"/reports/2021-06-30/documents/{report_doc_id}"
        rdt = await self.get_restricted_data_token("GET", resource_path, report_type=report_type)
        doc = await self.get_report_document(report_doc_id, rdt_token=rdt)
        data = await self.download_bytes(doc.url)
        if (doc.compressionAlgorithm or "").upper() == "GZIP":
            return await asyncio.to_thread(gunzip_to_text, data)
        return data.decode("utf-8", errors="replace")

    async def run_report(self, shop, report_type, *, report_options=None, start_date=None,
                         end_date=None, section="reports") -> ReportRun:
        """Cadena completa: create -> poll hasta estado terminal -> download.

        - DONE sin documento (período sin datos): devuelve ReportRun con
          content=None.
        - CANCELLED/FATAL (fallo real del reporte en Amazon): lanza
          AmazonAPIError. SIN esto, como esos estados terminales tampoco traen
          reportDocumentId, se devolvía content=None y los llamadores lo
          tomaban por «sin datos» (orders: «Sin pedidos…»; vat: «sin
          transacciones»), tragándose el fallo en silencio.
        - Si el polling agota los intentos propaga AmazonReportNotReadyError;
          los errores de creación propagan AmazonAPIError (con status_code).
        """
        report_id = await self.create_report(
            shop, report_type, report_options=report_options,
            start_date=start_date, end_date=end_date,
        )
        status = await self.get_report_status(report_id, section=section)
        if status.processingStatus in ("CANCELLED", "FATAL"):
            # Los reportes FATAL suelen traer un documento con la EXPLICACIÓN
            # del fallo (p.ej. «seller not enrolled in VAT Calculation
            # Service»). Descargarlo es best-effort: si falla, el error
            # principal (el estado terminal) no debe quedar enmascarado.
            detail = ""
            if status.reportDocumentId:
                try:
                    explanation = await self.download_report_content(status.reportDocumentId, report_type)
                    if explanation and explanation.strip():
                        detail = f" Detalle de Amazon: {explanation.strip()[:500]}"
                except Exception:
                    pass
            raise AmazonAPIError(
                f"Reporte {report_type} terminó en estado {status.processingStatus} (id {report_id}).{detail}"
            )
        if not status.reportDocumentId:
            return ReportRun(reportId=report_id)
        content = await self.download_report_content(status.reportDocumentId, report_type)
        return ReportRun(reportId=report_id, reportDocumentId=status.reportDocumentId, content=content)

    # ── Feeds ────────────────────────────────────────────────────────────────
    async def create_feed_document(self, content_type="application/json", content_encoding=None) -> CreateFeedDocumentResponse:
        # OJO: CreateFeedDocumentSpecification (2021-06-30) SOLO admite
        # contentType. `contentEncoding` no es un campo del spec — Amazon lo
        # ignora. Default None para no enviarlo; se mantiene el parámetro por
        # compatibilidad, pero declarar gzip aquí no comprime nada.
        url = f"{self._endpoint}/feeds/2021-06-30/documents"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        body = {"contentType": content_type}
        if content_encoding:
            body["contentEncoding"] = content_encoding
        resp = await self._call("post", url, "POST /feeds/2021-06-30/documents", extra_headers=headers, json=body)
        return CreateFeedDocumentResponse.model_validate(resp.json())

    async def send_feed(self, shop, feed_document_id, feed_type="JSON_LISTINGS_FEED") -> CreateFeedResponse:
        url = f"{self._endpoint}/feeds/2021-06-30/feeds"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        body = {"feedType": feed_type, "marketplaceIds": [shop], "inputFeedDocumentId": feed_document_id}
        resp = await self._call("post", url, "POST /feeds/2021-06-30/feeds", extra_headers=headers, json=body)
        return CreateFeedResponse.model_validate(resp.json())

    async def get_feed_status(self, feed_id, section="feeds") -> FeedStatusResponse:
        async def _check():
            url = f"{self._endpoint}/feeds/2021-06-30/feeds/{feed_id}"
            headers = {"Content-Type": "application/json; charset=utf-8"}
            resp = await self._call("get", url, "GET /feeds/2021-06-30/feeds/{id}", extra_headers=headers)
            result = FeedStatusResponse.model_validate(resp.json())
            if result.processingStatus not in _TERMINAL:
                raise AmazonFeedNotReadyError(result.processingStatus)
            return result
        return await self._poll(section, AmazonFeedNotReadyError, _check)

    async def get_feed_result_document(self, result_document_id) -> FeedDocumentResponse:
        url = f"{self._endpoint}/feeds/2021-06-30/documents/{result_document_id}"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        resp = await self._call("get", url, "GET /feeds/2021-06-30/documents/{id}", extra_headers=headers)
        return FeedDocumentResponse.model_validate(resp.json())

    async def send_tracking_feed(self, shop, file_path) -> CreateFeedResponse:
        from library.logging_helpers import info

        def _read(path):
            with open(path, "rb") as f:
                return f.read()

        ct = "text/tab-separated-values; charset=utf-8"
        create_res = await self.create_feed_document(content_type=ct, content_encoding=None)
        data = await asyncio.to_thread(_read, file_path)
        status = await self.s3_put(create_res.url, data, ct)
        if status != 200:
            # Sin esta comprobación se seguía a send_feed con un documento vacío
            # (feed sin TSV) y, peor, trackings._archive_and_cleanup borraba el
            # fichero de origen -> pérdida de datos. Igual que el flujo de stock.
            raise AmazonAPIError(
                f"Fallo subiendo el TSV de trackings a S3 (HTTP {status})", status_code=status
            )
        info(f"📤 Archivo cargado (ID: {create_res.feedDocumentId})")
        result = await self.send_feed(shop, create_res.feedDocumentId, feed_type="POST_FLAT_FILE_FULFILLMENT_DATA")
        info(f"✅ Feed creado exitosamente: {result.feedId}")
        return result

    # ── descargas / subidas crudas (S3 pre-firmado: sin token ni limiter) ──────
    # Estas operaciones van por httpx directo (no por el transporte), así que el
    # volcado debug del transporte NO las registra: en modo debug parecían un
    # hueco mudo entre dos pasos. Logueamos aquí con debug() (solo sale si
    # mode=debug) para que la subida/descarga a S3 sea visible.
    #
    # Pase 3: reintento propio (red + 5xx). El transporte no cubre estas rutas
    # y un parpadeo de red en la descarga final tiraba un documento que Amazon
    # ya había generado.
    async def _s3_request(self, method, url, **kwargs) -> httpx.Response:
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(_S3_ATTEMPTS),
            wait=_S3_WAIT,
            retry=retry_if_exception_type(_S3_RETRYABLE),
            reraise=True,
        ):
            with attempt:
                resp = await self._http.request(method, url, **kwargs)
                if resp.status_code >= 500:
                    raise AmazonServerError(
                        f"S3 {method.upper()} HTTP {resp.status_code}",
                        status_code=resp.status_code, body=resp.text,
                    )
                return resp

    async def s3_put(self, url, data, content_type, content_encoding=None) -> int:
        from library.logging_helpers import debug
        headers = {"Content-Type": content_type}
        if content_encoding:
            headers["Content-Encoding"] = content_encoding
        debug(f"S3 PUT {url[:80]}… ({len(data)} bytes)")
        resp = await self._s3_request("put", url, content=data, headers=headers)
        debug(f"S3 PUT -> {resp.status_code}")
        return resp.status_code

    async def download_text(self, url) -> str:
        from library.logging_helpers import debug
        debug(f"S3 GET {url[:80]}…")
        resp = await self._s3_request("get", url)
        if resp.status_code >= 400:
            raise AmazonAPIError(
                f"S3 GET HTTP {resp.status_code}", status_code=resp.status_code, body=resp.text
            )
        debug(f"S3 GET -> {resp.status_code} ({len(resp.content)} bytes)")
        return resp.text

    async def download_bytes(self, url) -> bytes:
        from library.logging_helpers import debug
        debug(f"S3 GET {url[:80]}…")
        resp = await self._s3_request("get", url)
        if resp.status_code >= 400:
            raise AmazonAPIError(
                f"S3 GET HTTP {resp.status_code}", status_code=resp.status_code, body=resp.text
            )
        debug(f"S3 GET -> {resp.status_code} ({len(resp.content)} bytes)")
        return resp.content

    async def download_feed_result_content(self, result_document_id) -> str:
        """Documento de resultado de un feed -> texto, respetando compressionAlgorithm.

        Unifica el bloque que stock._verify_feed y trackings duplicaban (tercera
        copia de la lógica gzip junto a download_report_content): un solo sitio
        que corregir si Amazon cambia el contrato de compresión.
        """
        from library.helper_functions import gunzip_to_text

        doc = await self.get_feed_result_document(result_document_id)
        raw = await self.download_bytes(doc.url)
        if (doc.compressionAlgorithm or "").upper() == "GZIP":
            return await asyncio.to_thread(gunzip_to_text, raw)
        return raw.decode("utf-8", errors="replace")
