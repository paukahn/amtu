"""Tests del token-bucket async (corrige B1: el limiter original nunca dormía).

No dormimos de verdad: parcheamos asyncio.sleep y verificamos la duración
calculada por el bucket.
"""

import unittest
from unittest.mock import AsyncMock, patch

from library.rate_limiter import AsyncTokenBucket


class TestRateLimiter(unittest.IsolatedAsyncioTestCase):
    async def test_no_rate_means_no_sleep(self):
        bucket = AsyncTokenBucket()  # sin rate conocido => passthrough
        with patch("asyncio.sleep", new_callable=AsyncMock) as sleep:
            await bucket.wait("eu", "GET /x")
            await bucket.wait("eu", "GET /x")
        sleep.assert_not_called()

    async def test_throttles_after_burst_is_drained(self):
        bucket = AsyncTokenBucket(default_burst=2)
        bucket.update("eu", "GET /x", {"x-amzn-RateLimit-Limit": "5"})  # 5/s, capacidad 2
        with patch("asyncio.sleep", new_callable=AsyncMock) as sleep:
            await bucket.wait("eu", "GET /x")  # 2 -> 1 fichas, sin dormir
            await bucket.wait("eu", "GET /x")  # 1 -> 0 fichas, sin dormir
            await bucket.wait("eu", "GET /x")  # vacío -> dormir ~1/5 = 0.2s
        self.assertEqual(sleep.call_count, 1)
        self.assertAlmostEqual(sleep.call_args.args[0], 0.2, delta=0.05)

    async def test_update_ignores_missing_or_invalid_header(self):
        bucket = AsyncTokenBucket()
        bucket.update("eu", "x", {})                                # ausente
        bucket.update("eu", "x", {"x-amzn-RateLimit-Limit": "abc"})  # no numérico
        bucket.update("eu", "x", {"x-amzn-RateLimit-Limit": "0"})    # no positivo
        with patch("asyncio.sleep", new_callable=AsyncMock) as sleep:
            await bucket.wait("eu", "x")
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
