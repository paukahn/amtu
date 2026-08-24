"""El flag `debug` debe fluir AccountClients -> AsyncTransport.

Regresión: en modo debug el transporte vuelca cada petición/respuesta a
consola (lo que antes hacía response_debugger.res_debug). El runner deriva
`debug` de common.ini (mode=debug) y lo pasa a AccountClients; si ese cableado
se rompe, en modo debug no sale NADA de depuración. Este test fija que
AccountClients reenvía el flag al transporte.
"""

import unittest
from unittest.mock import patch

from library import factory


class _FakeTokenProvider:
    def __init__(self, *args, **kwargs):
        self.markets = ["eu"]


class TestFactoryDebugFlag(unittest.TestCase):
    def test_debug_flag_reaches_transport(self):
        with patch.object(factory, "AsyncTokenProvider", _FakeTokenProvider):
            clients = factory.AccountClients(
                "app", "cuenta", key=b"k", hmac_key=b"h", polling_cfg=object(), debug=True,
            )
            try:
                self.assertTrue(clients._transport._debug)
            finally:
                import asyncio
                asyncio.run(clients.aclose())

    def test_debug_defaults_to_false(self):
        with patch.object(factory, "AsyncTokenProvider", _FakeTokenProvider):
            clients = factory.AccountClients(
                "app", "cuenta", key=b"k", hmac_key=b"h", polling_cfg=object(),
            )
            try:
                self.assertFalse(clients._transport._debug)
            finally:
                import asyncio
                asyncio.run(clients.aclose())


if __name__ == "__main__":
    unittest.main()
