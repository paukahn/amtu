"""read_remote_file: reintento ante fallos transitorios (pase 3d).

Regresión real de producción: un único intento sin retry; un ReadTimeout
puntual entre el servidor y Google Sheets (confirmado transitorio — la misma
URL respondió en <1s segundos después) tiraba la cuenta entera. Se prueba con
`unittest.mock.patch` sobre `httpx.get` (sin red real) y con la estrategia de
espera de tenacity forzada a no dormir, igual que hace test_transport.py.
"""

import unittest
from unittest.mock import patch

import httpx
from tenacity import wait_none

from library import file_explorer


class TestReadRemoteFileRetry(unittest.TestCase):
    def setUp(self):
        # No dormir segundos reales en los tests: se sustituyen las dos
        # estrategias de espera por wait_none() (objeto real de tenacity,
        # soporta el operador '+' que usa la suma exponencial+jitter del
        # código bajo prueba — a diferencia de una lambda simple).
        self._patchers = [
            patch("library.file_explorer.wait_exponential", return_value=wait_none()),
            patch("library.file_explorer.wait_random", return_value=wait_none()),
        ]
        for p in self._patchers:
            p.start()

    def tearDown(self):
        for p in self._patchers:
            p.stop()

    def test_transient_timeout_then_success_is_retried(self):
        ok_response = httpx.Response(200, text="sku\tPrice\nSKU1\t10.50\n", request=httpx.Request("GET", "http://x"))
        calls = {"n": 0}

        def fake_get(url, timeout=None, follow_redirects=None):
            calls["n"] += 1
            if calls["n"] == 1:
                raise httpx.ReadTimeout("timed out")
            return ok_response

        with patch("library.file_explorer.httpx.get", side_effect=fake_get):
            df = file_explorer.read_remote_file("http://x/stock.tsv")

        self.assertEqual(calls["n"], 2)  # 1 fallo transitorio + 1 éxito
        self.assertEqual(df.iloc[0]["sku"], "SKU1")

    def test_persistent_timeout_exhausts_retries_and_raises(self):
        def fake_get(url, timeout=None, follow_redirects=None):
            raise httpx.ReadTimeout("timed out")

        with patch("library.file_explorer.httpx.get", side_effect=fake_get) as mocked:
            with self.assertRaises(RuntimeError) as ctx:
                file_explorer.read_remote_file("http://x/stock.tsv")

        self.assertEqual(mocked.call_count, 3)  # agota los 3 intentos, no más
        self.assertIn("timed out", str(ctx.exception))

    def test_404_is_not_retried(self):
        # Un enlace/gid realmente roto no se arregla reintentando.
        bad_response = httpx.Response(404, text="Not Found", request=httpx.Request("GET", "http://x"))

        def fake_get(url, timeout=None, follow_redirects=None):
            return bad_response

        with patch("library.file_explorer.httpx.get", side_effect=fake_get) as mocked:
            with self.assertRaises(RuntimeError):
                file_explorer.read_remote_file("http://x/stock.tsv")

        self.assertEqual(mocked.call_count, 1)  # sin reintentos ante 404

    def test_transient_5xx_is_retried(self):
        bad_response = httpx.Response(503, text="upstream error", request=httpx.Request("GET", "http://x"))
        ok_response = httpx.Response(200, text="sku\tPrice\nSKU1\t10.50\n", request=httpx.Request("GET", "http://x"))
        calls = {"n": 0}

        def fake_get(url, timeout=None, follow_redirects=None):
            calls["n"] += 1
            return bad_response if calls["n"] == 1 else ok_response

        with patch("library.file_explorer.httpx.get", side_effect=fake_get):
            df = file_explorer.read_remote_file("http://x/stock.tsv")

        self.assertEqual(calls["n"], 2)
        self.assertEqual(df.iloc[0]["sku"], "SKU1")


if __name__ == "__main__":
    unittest.main()
