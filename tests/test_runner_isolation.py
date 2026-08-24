"""Aislamiento de fallos por cuenta en el runner.

Regresión (alta): el pase 2 movió la construcción de AccountClients al runner
envuelta solo en `except (ConfigError, ValueError)`, y el gather no usaba
return_exceptions. Un fallo inesperado al construir los clientes de UNA cuenta
escapaba de `guarded`, atravesaba el gather y tumbaba el LOTE entero. El pase 1
aislaba cualquier excepción por cuenta. Este test fija que una cuenta que
revienta en construcción no impide procesar a las demás.
"""

import unittest
from unittest.mock import patch

from library import runner


class TestRunnerIsolation(unittest.IsolatedAsyncioTestCase):
    async def test_unexpected_construction_error_does_not_kill_batch(self):
        accounts = {
            "buena1": {"aplicacion": "app", "modulos": ["orders"]},
            "mala":   {"aplicacion": "app", "modulos": ["orders"]},
            "buena2": {"aplicacion": "app", "modulos": ["orders"]},
        }
        processed = []

        class FakeClients:
            def __init__(self, app, name, **kwargs):
                # 'mala' revienta con un error que NO es ConfigError/ValueError.
                if name == "mala":
                    raise RuntimeError("boom inesperado")
                self.account = name

            async def __aenter__(self):
                return self

            async def __aexit__(self, *exc):
                return False

        async def fake_process(clients, name, info, ctx):
            processed.append(name)

        with patch.object(runner, "load_master_keys", return_value=(b"k", b"h")), \
             patch.object(runner.AccountsConfig, "__new__"), \
             patch.object(runner, "AccountClients", FakeClients), \
             patch.object(runner, "PollingConfig"), \
             patch.object(runner, "CommonConfig"):
            # AccountsConfig("config").get_all_accounts() -> accounts
            inst = runner.AccountsConfig.__new__.return_value
            inst.get_all_accounts.return_value = accounts
            runner.CommonConfig.return_value.get_mode.return_value = "production"

            # No debe lanzar pese a que 'mala' revienta en construcción.
            await runner.run_module("orders", fake_process, max_concurrency=2)

        # Las dos cuentas buenas se procesaron; el lote NO se cayó.
        self.assertEqual(sorted(processed), ["buena1", "buena2"])


if __name__ == "__main__":
    unittest.main()
