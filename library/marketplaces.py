"""Único punto de verdad de los metadatos de marketplaces de Amazon.

Sustituye a library/account_helpers/account_parameters.py (IDs de marketplace
+ endpoints) y a las tablas currency/region_of_country/locale_of_country de
library/helper_functions.py, que estaban DESINCRONIZADAS: la tabla de IDs
conocía 19 países pero las de región/moneda solo 10, de modo que tiendas como
'be' o 'nl' tenían marketplace ID pero `region_of_country` devolvía None y los
módulos las saltaban EN SILENCIO.

Si Amazon añade un marketplace, se añade UNA fila aquí.
"""

from __future__ import annotations

from typing import NamedTuple, Optional


class Marketplace(NamedTuple):
    marketplace_id: str
    region: str      # "EU" | "NA" (endpoint SP-API que la sirve)
    currency: str
    locale: str


MARKETPLACES: dict[str, Marketplace] = {
    # ── Región EU ────────────────────────────────────────────────
    "es": Marketplace("A1RKKUPIHCS9HS", "EU", "EUR", "es_ES"),   # España
    "fr": Marketplace("A13V1IB3VIYZZH", "EU", "EUR", "fr_FR"),   # Francia
    "de": Marketplace("A1PA6795UKMFR9", "EU", "EUR", "de_DE"),   # Alemania
    "it": Marketplace("APJ6JRA9NG5V4",  "EU", "EUR", "it_IT"),   # Italia
    "uk": Marketplace("A1F83G8C2ARO7P", "EU", "GBP", "en_GB"),   # Reino Unido
    "be": Marketplace("AMEN7PMS3EDWL",  "EU", "EUR", "fr_BE"),   # Bélgica
    "nl": Marketplace("A1805IZSGTT6HS", "EU", "EUR", "nl_NL"),   # Países Bajos
    "se": Marketplace("A2NODRKZP88ZB9", "EU", "SEK", "sv_SE"),   # Suecia
    "za": Marketplace("AE08WJ6YKNBMC",  "EU", "ZAR", "en_ZA"),   # Sudáfrica
    "pl": Marketplace("A1C3SOZRARQ6R3", "EU", "PLN", "pl_PL"),   # Polonia
    "eg": Marketplace("ARBP9OOSHTCHU",  "EU", "EGP", "ar_EG"),   # Egipto
    "tr": Marketplace("A33AVAJ2PDY3EV", "EU", "TRY", "tr_TR"),   # Turquía
    "sa": Marketplace("A17E79C6D8DWNP", "EU", "SAR", "ar_SA"),   # Arabia Saudita
    "ae": Marketplace("A2VIGQ35RCS4UG", "EU", "AED", "ar_AE"),   # Emiratos Árabes Unidos
    "in": Marketplace("A21TJRUUN4KGV",  "EU", "INR", "en_IN"),   # India
    # ── Región NA ────────────────────────────────────────────────
    "us": Marketplace("ATVPDKIKX0DER",  "NA", "USD", "en_US"),   # Estados Unidos
    "ca": Marketplace("A2EUQ1WTGCTBG2", "NA", "CAD", "en_CA"),   # Canadá
    "mx": Marketplace("A1AM78C64UM0Y8", "NA", "MXN", "es_MX"),   # México
    "br": Marketplace("A2Q3Y263D00KWC", "NA", "BRL", "pt_BR"),   # Brasil
}

_ENDPOINTS = {
    "eu": {"endpoint": "https://sellingpartnerapi-eu.amazon.com", "region": "eu-west-1"},
    "na": {"endpoint": "https://sellingpartnerapi-na.amazon.com", "region": "us-east-1"},
}

# Entorno de pruebas de la SP-API (pase 3): mismas rutas, host sandbox.
# Se selecciona con `environment = sandbox` en config/common.ini.
_SANDBOX_ENDPOINTS = {
    "eu": "https://sandbox.sellingpartnerapi-eu.amazon.com",
    "na": "https://sandbox.sellingpartnerapi-na.amazon.com",
}


def get_marketplace(code: str) -> Optional[Marketplace]:
    if not code:
        return None
    return MARKETPLACES.get(code.strip().lower())


def get_store_identifier(code: str) -> Optional[str]:
    mp = get_marketplace(code)
    return mp.marketplace_id if mp else None


def region_of_country(country_code: str) -> Optional[str]:
    mp = get_marketplace(country_code)
    return mp.region if mp else None


def currency(country_code: str) -> Optional[str]:
    mp = get_marketplace(country_code)
    return mp.currency if mp else None


def locale_of_country(country_code: str) -> Optional[str]:
    mp = get_marketplace(country_code)
    return mp.locale if mp else None


def get_market_endpoints(market: str, environment: str = "production") -> dict:
    """Endpoint SP-API + región AWS + tiendas de un mercado ('eu' | 'na').

    `environment`: 'production' (defecto) o 'sandbox'.
    """
    market = (market or "").lower()
    if market not in _ENDPOINTS:
        raise ValueError(f"Market desconocido: {market}")
    environment = (environment or "production").lower()
    if environment not in ("production", "sandbox"):
        raise ValueError(f"Environment desconocido: {environment}")
    info = dict(_ENDPOINTS[market])
    if environment == "sandbox":
        info["endpoint"] = _SANDBOX_ENDPOINTS[market]
    info["stores"] = [code for code, mp in MARKETPLACES.items() if mp.region == market.upper()]
    return info
