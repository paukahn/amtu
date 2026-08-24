"""key_manager: permisos (solo warning) y fuentes de llaves (pase 3).

Decisión registrada: el chequeo de permisos NUNCA falla — el cron corre bajo
un usuario sin privilegios y app_control se ejecuta bajo ese mismo usuario,
así que un fallo por permisos solo podría bloquear producción sin aportar
nada. «Legible por otros» genera un warning en el log; grupo (0640) ni eso.
La detección se prueba vía la función pura _is_world_readable (corre también
en Windows); la lectura por variable de entorno se prueba entera.
"""

import base64
import os
import unittest
from unittest.mock import patch

from library.security import key_manager


class TestWorldReadableDetection(unittest.TestCase):
    def test_owner_and_group_modes_are_quiet(self):
        # 0600/0400 (solo propietario) y 0640/0660 (compartido por grupo con
        # el usuario del cron): sin warning.
        for mode in (0o600, 0o400, 0o640, 0o660):
            self.assertFalse(key_manager._is_world_readable(mode), oct(mode))

    def test_world_readable_modes_warn(self):
        for mode in (0o644, 0o604, 0o646, 0o777):
            self.assertTrue(key_manager._is_world_readable(mode), oct(mode))

    def test_warn_helper_never_raises(self):
        # Aunque el fichero no exista o los permisos sean «malos», la función
        # jamás lanza: cargar las llaves no puede romperse por el chequeo.
        key_manager._warn_if_world_readable("no_existe_xyz.bin")


class TestEnvVarKeys(unittest.TestCase):
    def test_master_keys_from_env_var(self):
        key, hmac_key = b"K" * 32, b"H" * 32
        encoded = base64.b64encode(key + hmac_key).decode("ascii")
        with patch.dict(os.environ, {key_manager.ENV_KEYS_VAR: encoded}):
            k, h = key_manager.load_keys(auto=True)
        self.assertEqual((k, h), (key, hmac_key))

    def test_env_var_with_wrong_length_rejected(self):
        encoded = base64.b64encode(b"corto").decode("ascii")
        with patch.dict(os.environ, {key_manager.ENV_KEYS_VAR: encoded}):
            with self.assertRaises(RuntimeError):
                key_manager.load_keys(auto=True)

    def test_env_var_with_invalid_base64_rejected(self):
        with patch.dict(os.environ, {key_manager.ENV_KEYS_VAR: "no-es-base64!!!"}):
            with self.assertRaises(RuntimeError):
                key_manager.load_keys(auto=True)


if __name__ == "__main__":
    unittest.main()
