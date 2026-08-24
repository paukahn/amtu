"""Tests del fallback de tipo de reporte en orders (_run_tsv).

Cubren el cambio del pase 2: el tipo alternativo
GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL solo se intenta cuando
Amazon RECHAZA el tipo (HTTP 400). Antes cualquier AmazonAPIError (incluido un
5xx transitorio) cambiaba de tipo de reporte en silencio.
"""

import unittest

from library.exceptions import AmazonAPIError, AmazonReportNotReadyError
from library.models import ReportRun
from orders import _run_tsv

FALLBACK_TYPE = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"


class FakeClient:
    def __init__(self, first_error=None):
        self.calls = []
        self._first_error = first_error

    async def run_report(self, mkt_ids, report_type, **_kw):
        self.calls.append(report_type)
        if self._first_error is not None and len(self.calls) == 1:
            raise self._first_error
        return ReportRun(reportId="R1", reportDocumentId="D1", content="order-id\tdata")


class TestOrdersFallback(unittest.IsolatedAsyncioTestCase):
    async def test_success_does_not_fall_back(self):
        client = FakeClient()
        rt, run = await _run_tsv(client, ["M"], "2026-01-01", "2026-01-14", is_na=False)
        self.assertEqual(rt, "GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING")
        self.assertEqual(client.calls, ["GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING"])
        self.assertEqual(run.content, "order-id\tdata")

    async def test_400_falls_back_to_general_type(self):
        client = FakeClient(first_error=AmazonAPIError("tipo no soportado", status_code=400))
        rt, run = await _run_tsv(client, ["M"], "2026-01-01", "2026-01-14", is_na=False)
        self.assertEqual(rt, FALLBACK_TYPE)
        self.assertEqual(client.calls, ["GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING", FALLBACK_TYPE])
        self.assertEqual(run.content, "order-id\tdata")

    async def test_other_errors_propagate_without_fallback(self):
        client = FakeClient(first_error=AmazonAPIError("error de servidor", status_code=503))
        with self.assertRaises(AmazonAPIError):
            await _run_tsv(client, ["M"], "2026-01-01", "2026-01-14", is_na=False)
        self.assertEqual(client.calls, ["GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING"])

    async def test_poll_exhaustion_degrades_to_none_not_fallback(self):
        # Polling agotado != tipo inválido: se degrada a None (como antes),
        # sin cambiar de tipo de reporte.
        client = FakeClient(first_error=AmazonReportNotReadyError("IN_PROGRESS"))
        rt, run = await _run_tsv(client, ["M"], "2026-01-01", "2026-01-14", is_na=False)
        self.assertEqual(rt, "GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING")
        self.assertIsNone(run)
        self.assertEqual(client.calls, ["GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING"])

    async def test_na_uses_shipping_type(self):
        client = FakeClient()
        rt, _run = await _run_tsv(client, ["M"], "2026-01-01", "2026-01-14", is_na=True)
        self.assertEqual(rt, "GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING")


if __name__ == "__main__":
    unittest.main()
