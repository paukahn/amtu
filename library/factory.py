"""Factory: ensambla los recursos async de una cuenta y produce AmazonClient.

Reemplaza el cableado manual repetido en cada `process_account`
(`auth = account_auth(...)`, `limiter = create_limiter()`, `reporter = CreateReport(...)`).
Comparte un único httpx.AsyncClient (pool de conexiones), un limiter y un
proveedor de tokens por cuenta; el limiter distingue mercados por su clave
`region:endpoint`, así que es seguro compartirlo entre mercados.

Pase 3:
- El limiter arranca sembrado con las cuotas OFICIALES de las operaciones que
  usa el proyecto (antes era passthrough hasta ver la primera cabecera
  x-amzn-RateLimit-Limit y la oleada inicial podía estrellarse en 429). La
  cabecera de Amazon sigue teniendo la última palabra.
- User-Agent identificativo, como piden las guías de la SP-API (antes iba el
  python-httpx/x.y por defecto).
- `environment` ('production' | 'sandbox', de common.ini) fluye hasta
  AmazonClient para elegir el endpoint.
"""

from __future__ import annotations

import platform

import httpx

from library.transport import AsyncTransport
from library.rate_limiter import AsyncTokenBucket
from library.auth_provider import AsyncTokenProvider
from library.spapi_client import AmazonClient

USER_AGENT = f"amtubb/2.0 (Language=Python; Platform={platform.system()})"

# Cuotas oficiales SP-API de las operaciones usadas: endpoint -> (rate/s, burst).
# Fuente: tabla "Usage Plans" de Reports 2021-06-30, Feeds 2021-06-30 y Tokens 2021-03-01.
SPAPI_SEED_LIMITS: dict[str, tuple[float, float]] = {
    "POST /reports/2021-06-30/reports": (0.0167, 15),
    "GET /reports/2021-06-30/reports/{id}": (2.0, 15),
    "GET /reports/2021-06-30/documents/{id}": (0.0167, 15),
    "POST /tokens/2021-03-01/restrictedDataToken": (1.0, 10),
    "POST /feeds/2021-06-30/documents": (0.5, 15),
    "POST /feeds/2021-06-30/feeds": (0.0083, 15),
    "GET /feeds/2021-06-30/feeds/{id}": (2.0, 15),
    "GET /feeds/2021-06-30/documents/{id}": (0.0222, 10),
}


class AccountClients:
    def __init__(self, application_name, account, *, key, hmac_key, polling_cfg,
                 debug=False, environment="production"):
        self._http = httpx.AsyncClient(headers={"User-Agent": USER_AGENT})
        self._limiter = AsyncTokenBucket(seed=SPAPI_SEED_LIMITS)
        self._transport = AsyncTransport(self._http, self._limiter, debug=debug)
        self._tokens = AsyncTokenProvider(application_name, account, self._http, key=key, hmac_key=hmac_key)
        self._polling = polling_cfg
        self._environment = environment
        self.account = account
        self.markets = self._tokens.markets

    def client(self, market) -> AmazonClient:
        return AmazonClient(
            market, self._transport, self._tokens, self._polling, self._http,
            environment=self._environment,
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc):
        await self.aclose()
