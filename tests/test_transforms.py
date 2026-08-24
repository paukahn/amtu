"""Golden tests de la transformación del feed de stock (sin red ni API).

Fijan la salida de stock_json_convert para garantizar que la descomposición
del pase 2 (library.stock_feed) no altera el feed generado.
Los tests de convert_json se eliminaron junto con el módulo brand_analytics.

Pase 3b: stock_json_convert devuelve (feed, out_of_range) — el segundo
elemento es lo que stock.py usa para avisar por correo de los SKU con precio
fuera de [min, max]. Todos los call sites se actualizan para desempaquetar.
"""

import unittest

import pandas as pd

from library.stock_feed import stock_json_convert, stock_sanity_check, _parse_locale_number


class TestParseLocaleNumber(unittest.TestCase):
    def test_dot_decimal_unchanged(self):
        self.assertEqual(_parse_locale_number("41.98"), 41.98)

    def test_comma_decimal_spanish_format(self):
        # El caso real confirmado en producción (Google Sheets en español).
        self.assertEqual(_parse_locale_number("41,98"), 41.98)
        self.assertEqual(_parse_locale_number("399,00"), 399.0)

    def test_european_thousands_dot_decimal_comma(self):
        self.assertEqual(_parse_locale_number("1.234,56"), 1234.56)

    def test_us_thousands_comma_decimal_dot(self):
        self.assertEqual(_parse_locale_number("1,234.56"), 1234.56)

    def test_plain_integer(self):
        self.assertEqual(_parse_locale_number("5"), 5.0)

    def test_garbage_still_raises_value_error(self):
        with self.assertRaises(ValueError):
            _parse_locale_number("abc")


class TestStockSanityCheck(unittest.TestCase):
    def test_passes_when_ratio_above_min(self):
        ok, reason = stock_sanity_check(n_in=100, n_msg=90, min_ratio=0.5, min_rows=10)
        self.assertTrue(ok)
        self.assertEqual(reason, "")

    def test_blocks_when_too_many_dropped(self):
        ok, reason = stock_sanity_check(n_in=100, n_msg=10, min_ratio=0.5, min_rows=10)
        self.assertFalse(ok)
        self.assertIn("10/100", reason)

    def test_small_feeds_skip_guard(self):
        # Por debajo de min_rows el ratio no es fiable: se deja pasar.
        ok, _ = stock_sanity_check(n_in=3, n_msg=1, min_ratio=0.5, min_rows=10)
        self.assertTrue(ok)

    def test_boundary_ratio_is_allowed(self):
        ok, _ = stock_sanity_check(n_in=100, n_msg=50, min_ratio=0.5, min_rows=10)
        self.assertTrue(ok)


class TestStockJsonConvert(unittest.TestCase):
    def test_builds_feed_with_stock_and_price(self):
        df = pd.DataFrame([{
            "EAN": "111", "sku": "SKU1", "quantity": "5",
            "handling-time": "2", "Price": "10.50", "product-type": "SHOES",
        }])
        feed, out_of_range = stock_json_convert(df, "ES", "SELLER1")

        self.assertEqual(feed["header"]["sellerId"], "SELLER1")
        self.assertEqual(feed["header"]["issueLocale"], "es_ES")
        self.assertEqual(len(feed["messages"]), 1)
        self.assertEqual(out_of_range, [])

        msg = feed["messages"][0]
        self.assertEqual(msg["sku"], "SKU1")
        self.assertEqual(msg["productType"], "SHOES")

        patches = {p["path"]: p for p in msg["patches"]}
        self.assertIn("/attributes/fulfillment_availability", patches)
        self.assertIn("/attributes/purchasable_offer", patches)

        fa = patches["/attributes/fulfillment_availability"]["value"][0]
        self.assertEqual(fa["quantity"], 5)
        self.assertEqual(fa["lead_time_to_ship_max_days"], 2)

        po = patches["/attributes/purchasable_offer"]["value"][0]
        self.assertEqual(po["currency"], "EUR")
        self.assertEqual(po["our_price"][0]["schedule"][0]["value_with_tax"], 10.5)

    def test_row_without_sku_is_skipped(self):
        df = pd.DataFrame([{"EAN": "111", "sku": "", "quantity": "5", "Price": "10"}])
        feed, out_of_range = stock_json_convert(df, "ES", "SELLER1")
        self.assertEqual(feed["messages"], [])
        self.assertEqual(out_of_range, [])

    def test_price_below_min_omits_product_and_reports_it(self):
        df = pd.DataFrame([{
            "EAN": "111", "sku": "SKU1", "Price": "5.00",
            "minimum-seller-allowed-price": "8.00", "maximum-seller-allowed-price": "20.00",
        }])
        feed, out_of_range = stock_json_convert(df, "ES", "SELLER1")
        self.assertEqual(feed["messages"], [])
        # Pase 3b: reportado con las cifras reales, para el correo de aviso.
        self.assertEqual(out_of_range, [{"sku": "SKU1", "ean": "111", "price": 5.0, "min": 8.0, "max": 20.0}])

    def test_price_above_max_omits_product_and_reports_it(self):
        df = pd.DataFrame([{
            "EAN": "111", "sku": "SKU1", "Price": "25.00",
            "minimum-seller-allowed-price": "8.00", "maximum-seller-allowed-price": "20.00",
        }])
        feed, out_of_range = stock_json_convert(df, "ES", "SELLER1")
        self.assertEqual(feed["messages"], [])
        self.assertEqual(out_of_range, [{"sku": "SKU1", "ean": "111", "price": 25.0, "min": 8.0, "max": 20.0}])

    def test_price_out_of_range_omits_even_with_stock(self):
        # Aunque haya stock, un precio fuera de rango omite el producto (y se
        # reporta con min=None ya que aquí solo hay tope máximo).
        df = pd.DataFrame([{
            "EAN": "111", "sku": "SKU1", "quantity": "5", "handling-time": "2",
            "Price": "100.00", "maximum-seller-allowed-price": "20.00",
        }])
        feed, out_of_range = stock_json_convert(df, "ES", "SELLER1")
        self.assertEqual(feed["messages"], [])
        self.assertEqual(out_of_range, [{"sku": "SKU1", "ean": "111", "price": 100.0, "min": None, "max": 20.0}])

    def test_price_within_range_publishes_with_bounds(self):
        df = pd.DataFrame([{
            "EAN": "111", "sku": "SKU1", "Price": "12.00",
            "minimum-seller-allowed-price": "8.00", "maximum-seller-allowed-price": "20.00",
        }])
        feed, out_of_range = stock_json_convert(df, "ES", "SELLER1")
        self.assertEqual(len(feed["messages"]), 1)
        self.assertEqual(out_of_range, [])
        po = feed["messages"][0]["patches"][0]["value"][0]
        self.assertEqual(po["our_price"][0]["schedule"][0]["value_with_tax"], 12.0)
        self.assertEqual(po["minimum_seller_allowed_price"][0]["schedule"][0]["value_with_tax"], 8.0)
        self.assertEqual(po["maximum_seller_allowed_price"][0]["schedule"][0]["value_with_tax"], 20.0)

    def test_price_equal_to_bound_is_allowed(self):
        # Límites inclusivos: precio == min (o == max) se publica, sin reporte.
        df = pd.DataFrame([{
            "EAN": "111", "sku": "SKU1", "Price": "8.00",
            "minimum-seller-allowed-price": "8.00", "maximum-seller-allowed-price": "20.00",
        }])
        feed, out_of_range = stock_json_convert(df, "ES", "SELLER1")
        self.assertEqual(len(feed["messages"]), 1)
        self.assertEqual(out_of_range, [])

    def test_stock_only_without_price_publishes(self):
        # Sin precio no hay validación de rango: el stock se publica igual.
        df = pd.DataFrame([{"EAN": "111", "sku": "SKU1", "quantity": "5", "handling-time": "1"}])
        feed, out_of_range = stock_json_convert(df, "ES", "SELLER1")
        self.assertEqual(len(feed["messages"]), 1)
        self.assertEqual(out_of_range, [])
        paths = [p["path"] for p in feed["messages"][0]["patches"]]
        self.assertEqual(paths, ["/attributes/fulfillment_availability"])

    def test_invalid_handling_time_defaults_to_zero(self):
        # Pase 3 (cambio deliberado): un handling-time no numérico degrada a
        # 0 días con warning, SIN descartar el quantity válido. La semántica
        # anterior (ValueError silencioso descartaba el patch entero) dejaba
        # el catálogo sin stock cuando el fichero remoto perdía esa columna.
        df = pd.DataFrame([{"EAN": "111", "sku": "SKU1", "quantity": "5", "handling-time": "abc"}])
        feed, out_of_range = stock_json_convert(df, "ES", "SELLER1")
        self.assertEqual(len(feed["messages"]), 1)
        self.assertEqual(out_of_range, [])
        fa = feed["messages"][0]["patches"][0]["value"][0]
        self.assertEqual(fa["quantity"], 5)
        self.assertEqual(fa["lead_time_to_ship_max_days"], 0)

    def test_missing_handling_time_column_publishes_with_zero(self):
        # Columna handling-time ausente ('' via row.get): quantity se publica
        # con 0 días — antes float('') tiraba TODO el patch de stock.
        df = pd.DataFrame([{"EAN": "111", "sku": "SKU1", "quantity": "7"}])
        feed, out_of_range = stock_json_convert(df, "ES", "SELLER1")
        self.assertEqual(len(feed["messages"]), 1)
        self.assertEqual(out_of_range, [])
        fa = feed["messages"][0]["patches"][0]["value"][0]
        self.assertEqual(fa["quantity"], 7)
        self.assertEqual(fa["lead_time_to_ship_max_days"], 0)

    def test_invalid_min_price_drops_price_patch_without_reporting(self):
        # Semántica heredada: min/max NO numérico descarta el patch de precio
        # entero (no se publica "sin mínimo") — esto NO es "fuera de rango"
        # (no hay cifras válidas que reportar), así que no genera aviso.
        df = pd.DataFrame([{
            "EAN": "111", "sku": "SKU1", "Price": "12.00",
            "minimum-seller-allowed-price": "abc",
        }])
        feed, out_of_range = stock_json_convert(df, "ES", "SELLER1")
        self.assertEqual(feed["messages"], [])
        self.assertEqual(out_of_range, [])

    def test_spanish_comma_decimal_price_is_published_not_dropped(self):
        # Regresión del bug real de producción: antes 'Price'='41,98' hacía
        # fallar float() con ValueError, y como también faltaba quantity, la
        # fila entera se perdía con "sin precio ni stock — omitido" pese a
        # que el precio SÍ estaba presente, solo en formato español.
        df = pd.DataFrame([{
            "EAN": "8431543119690", "sku": "B0BZS4M2C7",
            "Price": "41,98", "minimum-seller-allowed-price": "39,99",
        }])
        feed, out_of_range = stock_json_convert(df, "ES", "SELLER1")
        self.assertEqual(len(feed["messages"]), 1)
        self.assertEqual(out_of_range, [])
        po = feed["messages"][0]["patches"][0]["value"][0]
        self.assertEqual(po["our_price"][0]["schedule"][0]["value_with_tax"], 41.98)
        self.assertEqual(po["minimum_seller_allowed_price"][0]["schedule"][0]["value_with_tax"], 39.99)

    def test_spanish_comma_decimal_out_of_range_is_still_detected(self):
        # La coma decimal no debe impedir detectar que el precio SÍ está
        # fuera de rango (antes de esta corrección, ni siquiera llegaba a
        # comparar: se perdía en el ValueError).
        df = pd.DataFrame([{
            "EAN": "111", "sku": "SKU1",
            "Price": "5,00", "minimum-seller-allowed-price": "8,00",
        }])
        feed, out_of_range = stock_json_convert(df, "ES", "SELLER1")
        self.assertEqual(feed["messages"], [])
        self.assertEqual(out_of_range, [{"sku": "SKU1", "ean": "111", "price": 5.0, "min": 8.0, "max": None}])

    def test_multiple_out_of_range_skus_are_all_reported(self):
        df = pd.DataFrame([
            {"EAN": "111", "sku": "SKU1", "Price": "5.00", "minimum-seller-allowed-price": "8.00"},
            {"EAN": "222", "sku": "SKU2", "Price": "12.00", "minimum-seller-allowed-price": "8.00"},
            {"EAN": "333", "sku": "SKU3", "Price": "99.00", "maximum-seller-allowed-price": "20.00"},
        ])
        feed, out_of_range = stock_json_convert(df, "ES", "SELLER1")
        self.assertEqual(len(feed["messages"]), 1)  # solo SKU2 (dentro de rango)
        self.assertEqual([o["sku"] for o in out_of_range], ["SKU1", "SKU3"])


if __name__ == "__main__":
    unittest.main()
