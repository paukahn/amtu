"""Runner compartido para los módulos (orders / stock / trackings / vat).

Orquestación async con concurrencia ACOTADA (asyncio.Semaphore). En el pase 2
el runner además CONSTRUYE los clientes de la cuenta: los cuatro módulos
repetían el mismo bloque try/except de inicialización de AccountClients y la
comprobación de 'aplicacion'. Ahora el contrato de `process_account` es

    async def process_account(clients, account_name, account_info, ctx)

donde `clients` es un AccountClients ya abierto (se cierra aquí) y `ctx` es un
RunContext con (key, hmac_key, polling_cfg) para lo que cada módulo necesite
construir aparte (p.ej. FTPConfig en orders).

Las clases de config ya no llaman a sys.exit(): lanzan ConfigError, que se
captura por cuenta — la captura de SystemExit del pase 1 sobra.

Pase 3:
- El cwd se ancla a la raíz del proyecto (cron/Programador arrancan desde
  otro directorio y el sistema creaba una «configuración paralela» vacía).
- Lock exclusivo por módulo: una segunda instancia simultánea (cron + manual)
  producía feeds duplicados y carreras sobre ficheros; ahora sale con aviso.
- Retención al arrancar: orders_backup (PII, 30 días por Amazon DPP), temp y
  logs se limpian según common.ini.
- `environment` (production|sandbox) fluye de common.ini a los clientes.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from library.security import load_master_keys
from library.factory import AccountClients
from library.paths import ensure_project_cwd
from library.proc_lock import ModuleLock
from library import housekeeping
from classes.config import AccountsConfig, CommonConfig, ConfigError, PollingConfig

DEFAULT_MAX_CONCURRENCY = 5


@dataclass(frozen=True)
class RunContext:
    key: bytes
    hmac_key: bytes
    polling_cfg: PollingConfig


async def run_module(
    module_name: str,
    process_account,
    *,
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    filter_by_module: bool = True,
):
    from library.logging_helpers import error, info, set_log_context

    try:
        key, hmac_key = load_master_keys()
    except Exception as e:
        error(f"Error cargando llaves: {e}")
        return
    try:
        accounts = AccountsConfig("config").get_all_accounts()
        polling_cfg = PollingConfig("config")
        common = CommonConfig("config")
        # En modo debug, el transporte vuelca cada petición/respuesta a consola
        # (con token redactado y cuerpo truncado). Antes de la migración eso lo
        # hacía library/debuggers/response_debugger.res_debug según el `mode` de
        # common.ini; ese cableado se perdió y el flag `debug` del transporte
        # quedaba SIEMPRE en False -> en modo debug no salía nada de debug.
        debug_mode = common.get_mode() == "debug"
        environment = common.get_environment()
    except ConfigError as e:
        error(f"Error cargando configuración: {e}")
        return

    if environment == "sandbox":
        info("🧪 Environment SANDBOX: las llamadas van a sandbox.sellingpartnerapi-*.amazon.com")

    # Retención best-effort (backups con PII, temp, logs) antes de trabajar.
    await asyncio.to_thread(housekeeping.run_retention, common)

    ctx = RunContext(key=key, hmac_key=hmac_key, polling_cfg=polling_cfg)

    if filter_by_module:
        eligible = {n: a for n, a in accounts.items() if module_name in a.get("modulos", [])}
    else:
        eligible = dict(accounts)

    if not eligible:
        # Sin esto, un accounts.ini roto (p.ej. contenido de otro fichero
        # pegado dentro) terminaba en un lote «exitoso» que no hizo NADA.
        error(
            f"Ninguna cuenta con el módulo '{module_name}' — nada que procesar. "
            f"Revisa accounts.ini (cuentas cargadas: {len(accounts)}).",
            type="warning",
        )
        return

    semaphore = asyncio.Semaphore(max_concurrency)

    async def guarded(name, account_info):
        async with semaphore:
            set_log_context(name)  # tag [cuenta] en cada línea de log de esta tarea
            try:
                # `except Exception` (no solo ConfigError/ValueError): la
                # construcción crea httpx/limiter/transport y lee config; un
                # fallo inesperado aquí NO debe escaparse, porque el gather de
                # abajo tumbaría el lote entero. Aísla por cuenta (como hacía el
                # pase 1, que envolvía todo el cuerpo en except Exception).
                #
                # to_thread: construir AccountClients descifra applications/
                # tokens (AES+HMAC) y lee disco — E/S bloqueante que no debe
                # correr en el event loop (mismo patrón que el resto del I/O).
                clients = await asyncio.to_thread(
                    AccountClients,
                    account_info.get("aplicacion"), name,
                    key=key, hmac_key=hmac_key, polling_cfg=polling_cfg, debug=debug_mode,
                    environment=environment,
                )
            except Exception as e:
                error(f"Error inicializando '{name}': {e}")
                return
            try:
                async with clients:
                    await process_account(clients, name, account_info, ctx)
            except Exception as e:
                error(f"Critical error in {module_name} for {name}: {e}")

    # return_exceptions=True: red de seguridad. `guarded` ya captura todo, pero
    # si algo fuera del try (semáforo, set_log_context) lanzara, esto evita que
    # una cuenta tumbe a las demás.
    await asyncio.gather(*(guarded(n, a) for n, a in eligible.items()), return_exceptions=True)


def run_module_sync(module_name: str, process_account, **kwargs) -> None:
    from library.logging_helpers import error

    # Anclar el cwd ANTES de tocar config/llaves: un cron sin «cd» arranca
    # desde otro directorio y crearía una configuración paralela vacía.
    ensure_project_cwd()

    # Una instancia por módulo: la segunda sale con aviso en vez de duplicar
    # feeds/entregas y pelearse por los mismos ficheros.
    lock = ModuleLock(module_name)
    if not lock.acquire():
        error(f"Otra instancia de '{module_name}' ya está en ejecución (locks/{module_name}.lock). Salgo.")
        return
    try:
        asyncio.run(run_module(module_name, process_account, **kwargs))
    finally:
        lock.release()
