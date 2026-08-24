"""_call valida el estado HTTP de TODAS las operaciones (pase 3).

Regresión: el transporte solo convertía 401/429/5xx en excepciones; un
400/403/404 llegaba al model_validate y estallaba como pydantic.ValidationError
mudo, perdiendo el cuerpo {"errors": ...} de Amazon. Ahora _call lo convierte
en AmazonAPIError(status_code, body) — y el fallback de orders (que distingue
por status_code == 400) sigue funcionando.
"""

import unittest

import httpx

from library.spapi_client import AmazonClient
from library.transport import AsyncTransport
from library.rate_limiter import AsyncTokenBucket
from library.exceptions import AmazonAPIError


class FakeTokens:
    async def get_access_token(self, market, force_refresh=False):
        return "TOKEN"


class FakePolling:
    def get_base_delay(self, _s): return 0.0
    def get_factor(self, _s): return 2.0
    def get_max_delay(self, _s): return 0.0
    def get_jitter(self, _s): return 0.0
    def get_max_attempts(self, _s): return 3


def build_client(handler):
    http = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://x")
    transport = AsyncTransport(http, AsyncTokenBucket())
    return AmazonClient("eu", transport, FakeTokens(), FakePolling(), http), http


class TestStatusErrors(unittest.IsolatedAsyncioTestCase):
    async def test_404_becomes_amazon_api_error_with_body(self):
        def handler(_req):
            return httpx.Response(404, json={"errors": [{"code": "NotFound", "message": "no such report"}]})

        client, http = build_client(handler)
        try:
            with self.assertRaises(AmazonAPIError) as ctx:
                await client.get_report_status("R404")
            self.assertEqual(ctx.exception.status_code, 404)
            self.assertIn("NotFound", ctx.exception.body)
        finally:
            await http.aclose()

    async def test_403_on_rdt_becomes_amazon_api_error(self):
        def handler(_req):
            return httpx.Response(403, json={"errors": [{"code": "Unauthorized", "message": "denied"}]})

        client, http = build_client(handler)
        try:
            with self.assertRaises(AmazonAPIError) as ctx:
                await client.get_restricted_data_token("GET", "/reports/2021-06-30/documents/D1")
            self.assertEqual(ctx.exception.status_code, 403)
        finally:
            await http.aclose()

    async def test_400_keeps_status_for_orders_fallback(self):
        def handler(_req):
            return httpx.Response(400, json={"errors": [{"code": "InvalidInput", "message": "bad type"}]})

        client, http = build_client(handler)
        try:
            with self.assertRaises(AmazonAPIError) as ctx:
                await client.create_report("M1", "TIPO_INEXISTENTE")
            self.assertEqual(ctx.exception.status_code, 400)
        finally:
            await http.aclose()

    async def test_invalid_input_400_captures_request_id_in_message_and_attribute(self):
        # Regresión real de producción: send_feed -> 400 InvalidInput con
        # details vacío (fallo conocido, intermitente, del lado de Amazon).
        # Sin el x-amzn-RequestId no hay forma de escalarlo a soporte de Amazon.
        def handler(_req):
            return httpx.Response(
                400,
                json={"errors": [{"code": "InvalidInput", "message": "Invalid request parameters", "details": ""}]},
                headers={"x-amzn-RequestId": "REQ-TRACKING-400"},
            )

        client, http = build_client(handler)
        try:
            with self.assertRaises(AmazonAPIError) as ctx:
                await client.send_feed("M1", "FD1", feed_type="POST_FLAT_FILE_FULFILLMENT_DATA")
            self.assertEqual(ctx.exception.request_id, "REQ-TRACKING-400")
            # También visible en str(e): trackings/orders/stock/vat solo hacen
            # f"{e}" en el log y en el correo — el id debe viajar EN el mensaje.
            self.assertIn("REQ-TRACKING-400", str(ctx.exception))
        finally:
            await http.aclose()

    async def test_no_request_id_header_omits_suffix_cleanly(self):
        def handler(_req):
            return httpx.Response(404, json={"errors": [{"code": "NotFound"}]})

        client, http = build_client(handler)
        try:
            with self.assertRaises(AmazonAPIError) as ctx:
                await client.get_report_status("R1")
            self.assertIsNone(ctx.exception.request_id)
            self.assertNotIn("None", str(ctx.exception))
        finally:
            await http.aclose()

    async def test_fatal_report_includes_amazon_explanation(self):
        # Un reporte FATAL con reportDocumentId debe descargar el documento de
        # error de Amazon e incluirlo en el mensaje (antes solo decía «FATAL»
        # y el operador no tenía ninguna pista del porqué).
        def handler(req):
            path = req.url.path
            if path == "/reports/2021-06-30/reports" and req.method == "POST":
                return httpx.Response(202, json={"reportId": "RF"})
            if path == "/reports/2021-06-30/reports/RF":
                return httpx.Response(200, json={
                    "reportId": "RF", "reportType": "GET_VAT_TRANSACTION_DATA",
                    "marketplaceIds": ["M"], "createdTime": "t",
                    "processingStatus": "FATAL", "reportDocumentId": "DERR",
                })
            if path == "/tokens/2021-03-01/restrictedDataToken":
                return httpx.Response(200, json={"restrictedDataToken": "RDT-1"})
            if path == "/reports/2021-06-30/documents/DERR":
                return httpx.Response(200, json={"reportDocumentId": "DERR", "url": "https://x/err-doc"})
            if path == "/err-doc":
                return httpx.Response(200, text="Seller is not enrolled in VAT Calculation Service")
            return httpx.Response(404, text=f"unexpected: {path}")

        client, http = build_client(handler)
        try:
            with self.assertRaises(AmazonAPIError) as ctx:
                await client.run_report("M1", "GET_VAT_TRANSACTION_DATA")
            self.assertIn("FATAL", str(ctx.exception))
            self.assertIn("not enrolled in VAT Calculation Service", str(ctx.exception))
        finally:
            await http.aclose()

    async def test_sandbox_environment_changes_endpoint(self):
        seen = []

        def handler(req):
            seen.append(str(req.url))
            return httpx.Response(202, json={"reportId": "R1"})

        http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        transport = AsyncTransport(http, AsyncTokenBucket())
        client = AmazonClient("eu", transport, FakeTokens(), FakePolling(), http, environment="sandbox")
        try:
            await client.create_report("M1", "TIPO")
            self.assertTrue(seen[0].startswith("https://sandbox.sellingpartnerapi-eu.amazon.com/"))
        finally:
            await http.aclose()


if __name__ == "__main__":
    unittest.main()
