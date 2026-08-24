"""Tests de AsyncTransport con httpx.MockTransport (sin red real)."""

import unittest

import httpx
from tenacity import wait_fixed

from library.transport import AsyncTransport
from library.exceptions import AmazonThrottleError, AmazonServerError, AmazonAuthError


def make_client(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://x")


class FakeLimiter:
    def __init__(self):
        self.waited = []
        self.updated = []

    async def wait(self, region, endpoint):
        self.waited.append((region, endpoint))

    def update(self, region, endpoint, headers):
        self.updated.append((region, endpoint))


class TestTransport(unittest.IsolatedAsyncioTestCase):
    async def test_200_ok_calls_limiter_and_returns(self):
        calls = {"n": 0}

        def handler(_request):
            calls["n"] += 1
            return httpx.Response(200, json={"ok": True})

        limiter = FakeLimiter()
        async with make_client(handler) as client:
            transport = AsyncTransport(client, limiter)
            resp = await transport.request("GET", "https://x/a", market="eu", endpoint_key="GET /a")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(calls["n"], 1)
        self.assertEqual(limiter.waited, [("eu", "GET /a")])
        self.assertEqual(len(limiter.updated), 1)

    async def test_429_then_200_is_retried(self):
        seq = [429, 200]

        def handler(_request):
            return httpx.Response(seq.pop(0), json={"ok": True})

        async with make_client(handler) as client:
            transport = AsyncTransport(client, FakeLimiter(), throttle_wait=wait_fixed(0), throttle_attempts=3)
            resp = await transport.request("GET", "https://x/a", market="eu", endpoint_key="k")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(seq, [])

    async def test_persistent_429_raises_throttle(self):
        def handler(_request):
            return httpx.Response(429, text="slow down")

        async with make_client(handler) as client:
            transport = AsyncTransport(client, FakeLimiter(), throttle_wait=wait_fixed(0), throttle_attempts=3)
            with self.assertRaises(AmazonThrottleError):
                await transport.request("GET", "https://x/a", market="eu", endpoint_key="k")

    async def test_500_then_200_is_retried(self):
        seq = [503, 200]

        def handler(_request):
            return httpx.Response(seq.pop(0), json={"ok": True})

        async with make_client(handler) as client:
            transport = AsyncTransport(client, FakeLimiter(), throttle_wait=wait_fixed(0), throttle_attempts=3)
            resp = await transport.request("GET", "https://x/a", market="eu", endpoint_key="k")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(seq, [])

    async def test_persistent_500_raises_server_error(self):
        def handler(_request):
            return httpx.Response(500, text="boom")

        async with make_client(handler) as client:
            transport = AsyncTransport(client, FakeLimiter(), throttle_wait=wait_fixed(0), throttle_attempts=3)
            with self.assertRaises(AmazonServerError) as ctx:
                await transport.request("GET", "https://x/a", market="eu", endpoint_key="k")

        self.assertEqual(ctx.exception.status_code, 500)

    async def test_network_error_then_200_is_retried(self):
        calls = {"n": 0}

        def handler(_request):
            calls["n"] += 1
            if calls["n"] == 1:
                raise httpx.ConnectError("connection refused")
            return httpx.Response(200, json={"ok": True})

        async with make_client(handler) as client:
            transport = AsyncTransport(client, FakeLimiter(), throttle_wait=wait_fixed(0), throttle_attempts=3)
            resp = await transport.request("GET", "https://x/a", market="eu", endpoint_key="k")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(calls["n"], 2)

    async def test_401_raises_auth_and_is_not_retried(self):
        calls = {"n": 0}

        def handler(_request):
            calls["n"] += 1
            return httpx.Response(401, text="unauthorized")

        async with make_client(handler) as client:
            transport = AsyncTransport(client, FakeLimiter(), throttle_wait=wait_fixed(0), throttle_attempts=3)
            with self.assertRaises(AmazonAuthError):
                await transport.request("GET", "https://x/a", market="eu", endpoint_key="k")

        self.assertEqual(calls["n"], 1)  # 401 no se reintenta

    async def test_quota_exceeded_in_body_is_throttled(self):
        seq = [
            httpx.Response(200, json={"errors": [{"code": "QuotaExceeded"}]}),
            httpx.Response(200, json={"ok": True}),
        ]

        def handler(_request):
            return seq.pop(0)

        async with make_client(handler) as client:
            transport = AsyncTransport(client, FakeLimiter(), throttle_wait=wait_fixed(0), throttle_attempts=3)
            resp = await transport.request("GET", "https://x/a", market="eu", endpoint_key="k")

        self.assertEqual(resp.json(), {"ok": True})
        self.assertEqual(seq, [])

    async def test_401_captures_request_id_for_amazon_support(self):
        # x-amzn-RequestId (pase 3f): lo primero que pide el soporte de Amazon
        # para investigar un caso — antes se descartaba con el resto de cabeceras.
        def handler(_request):
            return httpx.Response(401, text="unauthorized", headers={"x-amzn-RequestId": "REQ-401-ABC"})

        async with make_client(handler) as client:
            transport = AsyncTransport(client, FakeLimiter(), throttle_wait=wait_fixed(0), throttle_attempts=3)
            with self.assertRaises(AmazonAuthError) as ctx:
                await transport.request("GET", "https://x/a", market="eu", endpoint_key="k")

        self.assertEqual(ctx.exception.request_id, "REQ-401-ABC")

    async def test_persistent_500_captures_request_id(self):
        def handler(_request):
            return httpx.Response(500, text="boom", headers={"x-amzn-RequestId": "REQ-500-XYZ"})

        async with make_client(handler) as client:
            transport = AsyncTransport(client, FakeLimiter(), throttle_wait=wait_fixed(0), throttle_attempts=3)
            with self.assertRaises(AmazonServerError) as ctx:
                await transport.request("GET", "https://x/a", market="eu", endpoint_key="k")

        self.assertEqual(ctx.exception.request_id, "REQ-500-XYZ")

    async def test_persistent_429_captures_request_id(self):
        def handler(_request):
            return httpx.Response(429, text="slow down", headers={"x-amzn-RequestId": "REQ-429-QQQ"})

        async with make_client(handler) as client:
            transport = AsyncTransport(client, FakeLimiter(), throttle_wait=wait_fixed(0), throttle_attempts=3)
            with self.assertRaises(AmazonThrottleError) as ctx:
                await transport.request("GET", "https://x/a", market="eu", endpoint_key="k")

        self.assertEqual(ctx.exception.request_id, "REQ-429-QQQ")

    async def test_missing_request_id_header_is_none_not_error(self):
        # Sin la cabecera (p.ej. un error de un proxy intermedio, no de Amazon),
        # request_id debe quedar en None limpiamente, sin lanzar ni escribir "None".
        def handler(_request):
            return httpx.Response(500, text="boom")

        async with make_client(handler) as client:
            transport = AsyncTransport(client, FakeLimiter(), throttle_wait=wait_fixed(0), throttle_attempts=3)
            with self.assertRaises(AmazonServerError) as ctx:
                await transport.request("GET", "https://x/a", market="eu", endpoint_key="k")

        self.assertIsNone(ctx.exception.request_id)


if __name__ == "__main__":
    unittest.main()
