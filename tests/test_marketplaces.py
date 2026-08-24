"""Tests del catálogo único de marketplaces (library/marketplaces.py).

Verifican la propiedad que motivó el módulo: TODO marketplace con ID tiene
también región, moneda y locale (antes 'be'/'nl'/'za'... tenían ID pero no
región y los módulos los saltaban en silencio).
"""

import unittest

from library.marketplaces import (
    MARKETPLACES,
    currency,
    get_market_endpoints,
    get_store_identifier,
    locale_of_country,
    region_of_country,
)


class TestMarketplaces(unittest.TestCase):
    def test_every_entry_is_complete(self):
        for code, mp in MARKETPLACES.items():
            self.assertTrue(mp.marketplace_id, code)
            self.assertIn(mp.region, ("EU", "NA"), code)
            self.assertEqual(len(mp.currency), 3, code)
            self.assertIn("_", mp.locale, code)

    def test_known_values_preserved(self):
        self.assertEqual(get_store_identifier("es"), "A1RKKUPIHCS9HS")
        self.assertEqual(get_store_identifier("us"), "ATVPDKIKX0DER")
        self.assertEqual(currency("ES"), "EUR")
        self.assertEqual(currency("UK"), "GBP")
        self.assertEqual(locale_of_country("ES"), "es_ES")
        self.assertEqual(region_of_country("us"), "NA")

    def test_previously_missing_countries_now_resolve(self):
        # El bug que motivó la unificación: estas tiendas tenían marketplace
        # ID pero region_of_country devolvía None y se saltaban en silencio.
        for code in ("be", "nl", "za", "eg", "tr", "sa", "ae", "in", "br"):
            self.assertIsNotNone(region_of_country(code), code)
            self.assertIsNotNone(currency(code), code)
            self.assertIsNotNone(locale_of_country(code), code)

    def test_inputs_are_normalized(self):
        self.assertEqual(get_store_identifier(" ES "), "A1RKKUPIHCS9HS")
        self.assertEqual(region_of_country("Be"), "EU")
        self.assertIsNone(get_store_identifier("xx"))
        self.assertIsNone(region_of_country(""))

    def test_endpoints_match_region_grouping(self):
        eu = get_market_endpoints("eu")
        na = get_market_endpoints("na")
        self.assertEqual(eu["endpoint"], "https://sellingpartnerapi-eu.amazon.com")
        self.assertEqual(na["endpoint"], "https://sellingpartnerapi-na.amazon.com")
        self.assertEqual(set(eu["stores"]), {c for c, m in MARKETPLACES.items() if m.region == "EU"})
        self.assertEqual(set(na["stores"]), {c for c, m in MARKETPLACES.items() if m.region == "NA"})
        with self.assertRaises(ValueError):
            get_market_endpoints("xx")


if __name__ == "__main__":
    unittest.main()
