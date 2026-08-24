"""Tests de AmazonClient: polling, refresh-on-401 y run_report, con fakes."""

import gzip
import unittest

import httpx

from library.spapi_client import AmazonClient
from library.transport import AsyncTransport
from library.rate_limiter import AsyncTokenBucket
from library.exceptions import AmazonAPIError


class FakeTokens:
    def __init__(self):
        self.calls = []  # registra el valor de force_refresh

    async def get_access_token(self, market, force_refresh=False):
        self.calls.append(force_refresh)
        return "TOKEN_REFRESHED" if force_refresh else "TOKEN"


class FakePolling:
    # base/max=0 => sin esperas reales en el test
    def get_base_delay(self, _s):
        return 0.0

    def get_factor(self, _s):
        return 2.0

    def get_max_delay(self, _s):
        return 0.0

    def get_jitter(self, _s):
        return 0.0

    def get_max_attempts(self, _s):
        return 5


def build_client(handler, market="eu"):
    http = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://x")
    transport = AsyncTransport(http, AsyncTokenBucket())
    client = AmazonClient(market, transport, FakeTokens(), FakePolling(), http)
    return client, http


def report_chain_handler(*, content_response, compression=None):
    """Handler que responde la cadena completa create->status->RDT->doc->S3."""
    def handler(req):
        path = req.url.path
        if path == "/reports/2021-06-30/reports" and req.method == "POST":
            return httpx.Response(202, json={"reportId": "R7"})
        if path == "/reports/2021-06-30/reports/R7":
            return httpx.Response(200, json={
                "reportId": "R7", "reportType": "T", "marketplaceIds": ["M"],
                "createdTime": "t", "processingStatus": "DONE", "reportDocumentId": "D7",
            })
        if path == "/tokens/2021-03-01/restrictedDataToken":
            return httpx.Response(200, json={"restrictedDataToken": "RDT-1"})
        if path == "/reports/2021-06-30/documents/D7":
            doc = {"reportDocumentId": "D7", "url": "https://x/doc-content"}
            if compression:
                doc["compressionAlgorithm"] = compression
            return httpx.Response(200, json=doc)
        if path == "/doc-content":
            return content_response()
        return httpx.Response(404, text=f"unexpected: {path}")
    return handler


class TestClient(unittest.IsolatedAsyncioTestCase):
    async def test_report_status_polls_until_terminal(self):
        seq = ["IN_PROGRESS", "DONE"]

        def handler(_req):
            status = seq.pop(0)
            return httpx.Response(200, json={
                "reportId": "R1",
                "reportType": "T",
                "marketplaceIds": ["M"],
                "createdTime": "t",
                "processingStatus": status,
                "reportDocumentId": "D1" if status == "DONE" else None,
            })

        client, http = build_client(handler)
        try:
            result = await client.get_report_status("R1")
        finally:
            await http.aclose()

        self.assertEqual(result.processingStatus, "DONE")
        self.assertEqual(result.reportDocumentId, "D1")
        self.assertEqual(seq, [])  # se consumieron ambas respuestas

    async def test_401_triggers_refresh_and_retry(self):
        seq = [401, 202]

        def handler(_req):
            code = seq.pop(0)
            if code == 401:
                return httpx.Response(401, text="unauthorized")
            return httpx.Response(202, json={"reportId": "R9"})

        client, http = build_client(handler)
        tokens = client._tokens
        try:
            report_id = await client.create_report(["M"], "GET_X")
        finally:
            await http.aclose()

        self.assertEqual(report_id, "R9")
        self.assertIn(True, tokens.calls)  # se forzó un refresh tras el 401

    async def test_run_report_full_chain_plain_document(self):
        handler = report_chain_handler(
            content_response=lambda: httpx.Response(200, text="order-id\tdata"),
        )
        client, http = build_client(handler)
        try:
            run = await client.run_report(["M"], "GET_X")
        finally:
            await http.aclose()

        self.assertEqual(run.reportId, "R7")
        self.assertEqual(run.reportDocumentId, "D7")
        self.assertEqual(run.content, "order-id\tdata")

    async def test_run_report_decompresses_gzip_document(self):
        payload = gzip.compress("vat\tdata".encode("utf-8"))
        handler = report_chain_handler(
            content_response=lambda: httpx.Response(200, content=payload),
            compression="GZIP",
        )
        client, http = build_client(handler)
        try:
            run = await client.run_report(["M"], "GET_VAT_TRANSACTION_DATA")
        finally:
            await http.aclose()

        self.assertEqual(run.content, "vat\tdata")

    async def test_run_report_without_document_returns_empty_content(self):
        def handler(req):
            path = req.url.path
            if path == "/reports/2021-06-30/reports" and req.method == "POST":
                return httpx.Response(202, json={"reportId": "R8"})
            if path == "/reports/2021-06-30/reports/R8":
                return httpx.Response(200, json={
                    "reportId": "R8", "reportType": "T", "marketplaceIds": ["M"],
                    "createdTime": "t", "processingStatus": "DONE", "reportDocumentId": None,
                })
            return httpx.Response(404, text="unexpected")

        client, http = build_client(handler)
        try:
            run = await client.run_report(["M"], "GET_X")
        finally:
            await http.aclose()

        self.assertEqual(run.reportId, "R8")
        self.assertIsNone(run.content)

    async def test_run_report_raises_on_terminal_failure(self):
        # CANCELLED/FATAL no debe tomarse por "sin datos" (content=None): debe
        # lanzar para que orders/vat lo traten como fallo, no como período vacío.
        for failed in ("CANCELLED", "FATAL"):
            def handler(req, _status=failed):
                path = req.url.path
                if path == "/reports/2021-06-30/reports" and req.method == "POST":
                    return httpx.Response(202, json={"reportId": "Rx"})
                if path == "/reports/2021-06-30/reports/Rx":
                    return httpx.Response(200, json={
                        "reportId": "Rx", "reportType": "T", "marketplaceIds": ["M"],
                        "createdTime": "t", "processingStatus": _status, "reportDocumentId": None,
                    })
                return httpx.Response(404, text="unexpected")

            client, http = build_client(handler)
            try:
                with self.assertRaises(AmazonAPIError):
                    await client.run_report(["M"], "GET_X")
            finally:
                await http.aclose()

    async def test_send_tracking_feed_raises_when_s3_put_fails(self):
        # Subida S3 fallida NO debe seguir a send_feed (feed vacío) ni dejar que
        # el llamador archive/borre el fichero de origen.
        import os
        import tempfile

        sent = {"send_feed": False}

        def handler(req):
            path = req.url.path
            if path == "/feeds/2021-06-30/documents" and req.method == "POST":
                return httpx.Response(200, json={"feedDocumentId": "FD1", "url": "https://x/s3-upload"})
            if path == "/s3-upload" and req.method == "PUT":
                return httpx.Response(403, text="expired")
            if path == "/feeds/2021-06-30/feeds":
                sent["send_feed"] = True
                return httpx.Response(201, json={"feedId": "F1"})
            return httpx.Response(404, text="unexpected")

        fd, tmp = tempfile.mkstemp(suffix=".tsv")
        os.write(fd, b"order-id\ttracking-number\n")
        os.close(fd)

        client, http = build_client(handler)
        try:
            with self.assertRaises(AmazonAPIError):
                await client.send_tracking_feed("M", tmp)
            self.assertFalse(sent["send_feed"])  # no se llamó a send_feed
        finally:
            await http.aclose()
            os.unlink(tmp)


if __name__ == "__main__":
    unittest.main()
