"""secret_keys.bin: formato v2 (PBKDF2-SHA256/600k + Encrypt-then-MAC) + compat v1.

ITERATIONS_V2 se baja a 1000 en los tests para no gastar ~0.5s por derivación
(la ruta real es interactiva por CLI, una sola vez).
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

from library.security import crypto_utils


class TestCryptoUtils(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "secret_keys.bin")
        self.key = b"K" * 32
        self.hmac_key = b"H" * 32
        # Parchear KEY_FILE e iteraciones (rápido) para todos los tests.
        self._patches = [
            patch.object(crypto_utils, "KEY_FILE", self.path),
            patch.object(crypto_utils, "ITERATIONS_V2", 1000),
            patch.object(crypto_utils, "ITERATIONS_V1", 1000),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()
        self.dir.cleanup()

    def test_v2_roundtrip(self):
        crypto_utils.encrypt_keys(self.key, self.hmac_key, "clave-maestra")
        with open(self.path, "rb") as f:
            blob = f.read()
        self.assertEqual(blob[0], crypto_utils.VERSION_V2)      # byte-versión
        self.assertNotIn(self.key, blob)                        # cifrado, no en claro
        k, h = crypto_utils.load_keys("clave-maestra")
        self.assertEqual((k, h), (self.key, self.hmac_key))

    def test_v2_wrong_password_rejected(self):
        crypto_utils.encrypt_keys(self.key, self.hmac_key, "buena")
        # Contraseña errónea: el HMAC no verifica -> v2 falla -> cae a v1 -> también
        # falla (unpad/len) -> excepción. NO debe devolver llaves basura.
        with self.assertRaises(Exception):
            crypto_utils.load_keys("mala")

    def test_v2_tamper_detected(self):
        crypto_utils.encrypt_keys(self.key, self.hmac_key, "clave")
        with open(self.path, "rb") as f:
            blob = bytearray(f.read())
        blob[40] ^= 0x01  # alterar un byte del ciphertext
        with open(self.path, "wb") as f:
            f.write(blob)
        with self.assertRaises(Exception):
            crypto_utils.load_keys("clave")

    def _write_v1(self, password, salt):
        derived = PBKDF2(password, salt, dkLen=32, count=crypto_utils.ITERATIONS_V1)
        cipher = AES.new(derived, AES.MODE_CBC)
        iv = cipher.iv
        ct = cipher.encrypt(crypto_utils.pad(self.key + self.hmac_key))
        with open(self.path, "wb") as f:
            f.write(salt + iv + ct)

    def test_legacy_v1_still_loads(self):
        # Fichero v1 a mano (sin byte-versión, SHA1/100k->aquí 1000, sin HMAC).
        password = "vieja-clave"
        self._write_v1(password, get_random_bytes(16))
        k, h = crypto_utils.load_keys(password)
        self.assertEqual((k, h), (self.key, self.hmac_key))

    def test_legacy_v1_with_salt_starting_0x02_still_loads(self):
        # Pase 3: el despacho es por LONGITUD (112=v1), así que un v1 cuya sal
        # empiece casualmente por el byte-versión de v2 ya no cae en la rama v2.
        password = "vieja-clave"
        salt = bytes([crypto_utils.VERSION_V2]) + get_random_bytes(15)
        self._write_v1(password, salt)
        k, h = crypto_utils.load_keys(password)
        self.assertEqual((k, h), (self.key, self.hmac_key))

    def test_unrecognizable_length_raises(self):
        with open(self.path, "wb") as f:
            f.write(b"\x02" + b"x" * 50)  # ni 112 ni 145 bytes
        with self.assertRaises(ValueError):
            crypto_utils.load_keys("da-igual")


if __name__ == "__main__":
    unittest.main()
