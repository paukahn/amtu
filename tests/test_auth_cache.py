"""Tests de la caché de access tokens por expires_in (library/auth_provider.py).

Cubren el cambio del pase 2: validez por `expires_at` real (con margen) en
fichero JSON, y compatibilidad con la caché antigua en texto plano (se trata
como caducada y fuerza UN refresh que la migra a JSON).
"""

import json
import os
import tempfile
import time
import unittest

from library.auth_provider import SAFETY_MARGIN, _read_cache, _still_valid, _write_cache


class TestTokenCache(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "sub", "access_token_eu")

    def tearDown(self):
        self.dir.cleanup()

    def test_roundtrip(self):
        expires_at = time.time() + 3600
        _write_cache(self.path, "TOK", expires_at)
        token, read_expires = _read_cache(self.path)
        self.assertEqual(token, "TOK")
        self.assertAlmostEqual(read_expires, expires_at, places=3)
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(set(json.load(f)), {"access_token", "expires_at"})

    def test_missing_file(self):
        self.assertEqual(_read_cache(self.path), (None, 0.0))

    def test_legacy_plaintext_file_is_expired(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("Atza|token-en-texto-plano")
        token, expires_at = _read_cache(self.path)
        self.assertIsNone(token)  # no es JSON válido -> caducado
        self.assertEqual(expires_at, 0.0)
        self.assertFalse(_still_valid(expires_at))

    def test_corrupt_json_is_expired(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write('{"access_token": "X"}')  # sin expires_at
        token, expires_at = _read_cache(self.path)
        self.assertIsNone(token)
        self.assertEqual(expires_at, 0.0)


class TestEncryptedTokenCache(unittest.TestCase):
    KEY = b"0" * 32
    HMAC = b"1" * 32

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "sub", "access_token_eu")

    def tearDown(self):
        self.dir.cleanup()

    def test_encrypted_roundtrip(self):
        expires_at = time.time() + 3600
        _write_cache(self.path, "TOK", expires_at, self.KEY, self.HMAC)
        # En disco NO debe quedar el token en claro.
        with open(self.path, "rb") as f:
            blob = f.read()
        self.assertNotIn(b"TOK", blob)
        token, read_expires = _read_cache(self.path, self.KEY, self.HMAC)
        self.assertEqual(token, "TOK")
        self.assertAlmostEqual(read_expires, expires_at, places=3)

    def test_wrong_key_is_expired(self):
        _write_cache(self.path, "TOK", time.time() + 3600, self.KEY, self.HMAC)
        token, expires_at = _read_cache(self.path, self.KEY, b"2" * 32)
        self.assertIsNone(token)
        self.assertEqual(expires_at, 0.0)

    def test_legacy_plaintext_read_with_keys_is_expired(self):
        # Caché antigua en claro leída con llaves: el descifrado falla -> caducado
        # -> se fuerza un refresh que la regenera cifrada (migración automática).
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"access_token": "OLD", "expires_at": time.time() + 3600}, f)
        token, expires_at = _read_cache(self.path, self.KEY, self.HMAC)
        self.assertIsNone(token)
        self.assertEqual(expires_at, 0.0)


class TestStillValid(unittest.TestCase):
    def test_respects_safety_margin(self):
        now = 1_000_000.0
        self.assertTrue(_still_valid(now + SAFETY_MARGIN + 1, now))
        self.assertFalse(_still_valid(now + SAFETY_MARGIN - 1, now))
        self.assertFalse(_still_valid(0.0, now))


if __name__ == "__main__":
    unittest.main()
