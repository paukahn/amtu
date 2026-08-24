"""_send_region_feed avisa por correo de los SKU con precio fuera de rango
(pase 3b, a petición del operador).

Antes solo quedaba un warning en el log de errores — fácil de pasar por alto
salvo que el volumen de SKU excluidos activara el sanity-guard (que bloquea
el feed entero, no avisa por cada SKU individual). Ahora cada ejecución con
al menos un SKU fuera de [min, max] dispara notify_error_mail, incluso cuando
TODOS los SKU quedan fuera de rango y el feed termina vacío.
"""

import unittest
from unittest.mock import patch

import pandas as pd

import stock


class FakeDoc:
    feedDocumentId = "FD1"
    url = "https://x/upload"


class FakeFeedResult:
    feedId = "F1"


class FakeClient:
    def __init__(self):
        self.sent = False

    async def create_feed_document(self, content_type="application/json"):
        return FakeDoc()

    async def s3_put(self, url, data, content_type):
        return 200

    async def send_feed(self, shop, feed_document_id):
        self.sent = True
        return FakeFeedResult()


class FakeStocksConfig:
    def get_seller_id(self, account_name, region):
        return "SELLER1"


class TestStockPriceAlert(unittest.IsolatedAsyncioTestCase):
    async def test_out_of_range_sku_triggers_email_and_feed_still_sent(self):
        df = pd.DataFrame([
            {"EAN": "111", "sku": "SKU1", "Price": "5.00", "minimum-seller-allowed-price": "8.00"},
            {"EAN": "222", "sku": "SKU2", "quantity": "5", "Price": "12.00", "minimum-seller-allowed-price": "8.00"},
        ])
        client = FakeClient()

        with patch.object(stock, "read_remote_file", return_value=df), \
             patch.object(stock, "notify_error_mail") as mock_mail, \
             patch.object(stock, "archive_sent_stock_tsv"):
            result = await stock._send_region_feed(
                client, FakeStocksConfig(), "cuenta", "cuenta", "ES", "http://x/stock.tsv", (0.5, 10),
            )

        # El SKU válido se sigue enviando: el aviso no bloquea el feed.
        self.assertEqual(result, ("ES", "F1"))
        self.assertTrue(client.sent)

        mock_mail.assert_called_once()
        subject, body = mock_mail.call_args[0]
        self.assertIn("cuenta", subject)
        self.assertIn("ES", subject)
        self.assertIn("SKU1", body)
        self.assertIn("5.0", body)
        self.assertIn("8.0", body)
        self.assertNotIn("SKU2", body)  # solo se reportan los excluidos

    async def test_no_out_of_range_skus_means_no_email(self):
        df = pd.DataFrame([{"EAN": "111", "sku": "SKU1", "quantity": "5", "Price": "12.00"}])
        client = FakeClient()

        with patch.object(stock, "read_remote_file", return_value=df), \
             patch.object(stock, "notify_error_mail") as mock_mail, \
             patch.object(stock, "archive_sent_stock_tsv"):
            await stock._send_region_feed(
                client, FakeStocksConfig(), "cuenta", "cuenta", "ES", "http://x/stock.tsv", (0.5, 10),
            )

        mock_mail.assert_not_called()

    async def test_all_skus_out_of_range_still_emails_even_though_feed_is_empty(self):
        # Caso límite: si TODOS los SKU quedan fuera de rango, el feed no
        # tiene mensajes y _send_region_feed corta pronto — el aviso debe
        # dispararse ANTES de ese corte, no depender de que sobrevivan filas.
        df = pd.DataFrame([
            {"EAN": "111", "sku": "SKU1", "Price": "5.00", "minimum-seller-allowed-price": "8.00"},
        ])
        client = FakeClient()

        with patch.object(stock, "read_remote_file", return_value=df), \
             patch.object(stock, "notify_error_mail") as mock_mail, \
             patch.object(stock, "archive_sent_stock_tsv"):
            result = await stock._send_region_feed(
                client, FakeStocksConfig(), "cuenta", "cuenta", "ES", "http://x/stock.tsv", (0.5, 10),
            )

        self.assertIsNone(result)  # sin mensajes válidos, no se envía nada
        self.assertFalse(client.sent)
        mock_mail.assert_called_once()  # pero el aviso SÍ salió


if __name__ == "__main__":
    unittest.main()
