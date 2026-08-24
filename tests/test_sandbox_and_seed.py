"""Sandbox de la SP-API y seed de cuotas del rate limiter (pase 3)."""

import asyncio
import unittest

from library.marketplaces import get_market_endpoints
from library.rate_limiter import AsyncTokenBucket


class TestSandboxEndpoints(unittest.TestCase):
    def test_production_default(self):
        info = get_market_endpoints("eu")
        self.assertEqual(info["endpoint"], "https://sellingpartnerapi-eu.amazon.com")

    def test_sandbox_eu_and_na(self):
        self.assertEqual(
            get_market_endpoints("eu", "sandbox")["endpoint"],
            "https://sandbox.sellingpartnerapi-eu.amazon.com",
        )
        self.assertEqual(
            get_market_endpoints("na", "sandbox")["endpoint"],
            "https://sandbox.sellingpartnerapi-na.amazon.com",
        )

    def test_unknown_environment_raises(self):
        with self.assertRaises(ValueError):
            get_market_endpoints("eu", "staging")


class TestLimiterSeed(unittest.TestCase):
    def test_seed_limits_before_first_header(self):
        # Con seed, la clave arranca limitada (antes: passthrough hasta ver la
        # primera cabecera x-amzn-RateLimit-Limit).
        bucket = AsyncTokenBucket(seed={"EP": (1.0, 2.0)})

        async def scenario():
            await bucket.wait("eu", "EP")
            await bucket.wait("eu", "EP")

        asyncio.run(scenario())
        # Tras 2 waits con burst 2, el cubo quedó (casi) vacío.
        self.assertLess(bucket._tokens["eu:EP"], 1.0)

    def test_seed_burst_used_as_capacity_on_header_update(self):
        bucket = AsyncTokenBucket(seed={"EP": (1.0, 7.0)})
        bucket.update("eu", "EP", {"x-amzn-RateLimit-Limit": "2.5"})
        self.assertEqual(bucket._rates["eu:EP"], 2.5)
        self.assertEqual(bucket._capacity["eu:EP"], 7.0)

    def test_no_seed_no_header_is_passthrough(self):
        bucket = AsyncTokenBucket()

        async def scenario():
            for _ in range(50):
                await bucket.wait("eu", "EP")

        asyncio.run(scenario())  # no debe dormir ni fallar
        self.assertNotIn("eu:EP", bucket._tokens)


if __name__ == "__main__":
    unittest.main()
