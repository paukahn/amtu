"""Smoke-test de tokens: refresca/imprime el access token de cada cuenta-mercado.

Migrado a AsyncTokenProvider. El original construía `Auth(app, account)` sin
pasar las llaves maestras (lo que en la práctica fallaba al descifrar las
credenciales); aquí se cargan con load_master_keys.
"""

import asyncio

import httpx

from classes.config import AccountsConfig
from library.auth_provider import AsyncTokenProvider
from library.security import load_master_keys
from library.logging_helpers import info, error


async def _warm_account(account_name, account_info, key, hmac_key):
    app_name = account_info.get("aplicacion")
    if not app_name:
        error(f"La cuenta '{account_name}' no tiene aplicación asignada.")
        return
    async with httpx.AsyncClient() as http:
        provider = AsyncTokenProvider(app_name, account_name, http, key=key, hmac_key=hmac_key)
        for market in provider.markets:
            try:
                token = await provider.get_access_token(market)
                # Sin contenido del token en logs: es un bearer vivo (el resto
                # del proyecto lo redacta con cuidado — aquí se filtraba un prefijo).
                info(f"[{account_name} - {market}] access token OK ({len(token)} chars)")
            except Exception as token_error:
                error(f"Error al obtener token para '{account_name}' en '{market}': {token_error}")


async def _main():
    try:
        key, hmac_key = load_master_keys()
        accounts_data = AccountsConfig("config").get_all_accounts()
    except Exception as e:
        error(f"Error de inicialización: {e}")
        return

    for account_name, account_info in accounts_data.items():
        try:
            await _warm_account(account_name, account_info, key, hmac_key)
        except Exception as e:
            error(f"Error con cuenta '{account_name}': {e}")


def main():
    from library.paths import ensure_project_cwd
    ensure_project_cwd()
    asyncio.run(_main())


if __name__ == "__main__":
    main()
