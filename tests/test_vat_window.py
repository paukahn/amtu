"""Ventana «mes anterior» del VAT: UTC y SIN cruzar la frontera de mes.

Regresión doble:
1. La ventana se calculaba con datetime.today() (hora LOCAL) pero se enviaba
   con sufijo 'Z'; un cron a las 00:xx del día 1 en Madrid podía pedir el mes
   equivocado. → cálculo en UTC (pase 3).
2. Un dataEndTime en el primer instante del mes CORRIENTE (frontera
   «exclusiva») hacía terminar GET_VAT_TRANSACTION_DATA en FATAL: Amazon
   exige el rango dentro de un único mes calendario. Verificado contra la
   versión síncrona original, que envía <último día>T23:59:59Z y funciona.
"""

import unittest
from datetime import datetime, timezone

from vat_report import _prev_month_window


class TestPrevMonthWindow(unittest.TestCase):
    def test_mid_month(self):
        now = datetime(2026, 7, 15, 10, 30, tzinfo=timezone.utc)
        start, end = _prev_month_window(now)
        self.assertEqual(start, "2026-06-01T00:00:00Z")
        self.assertEqual(end, "2026-06-30T23:59:59Z")

    def test_first_instant_of_month(self):
        # Justo después de medianoche UTC del día 1: el «mes anterior» es junio.
        now = datetime(2026, 7, 1, 0, 0, 5, tzinfo=timezone.utc)
        start, end = _prev_month_window(now)
        self.assertEqual(start, "2026-06-01T00:00:00Z")
        self.assertEqual(end, "2026-06-30T23:59:59Z")

    def test_year_boundary(self):
        now = datetime(2026, 1, 10, tzinfo=timezone.utc)
        start, end = _prev_month_window(now)
        self.assertEqual(start, "2025-12-01T00:00:00Z")
        self.assertEqual(end, "2025-12-31T23:59:59Z")

    def test_window_never_crosses_month_boundary(self):
        # La restricción que rompió producción: start y end deben compartir
        # mes calendario (YYYY-MM), o Amazon devuelve FATAL.
        for month in range(1, 13):
            now = datetime(2026, month, 15, tzinfo=timezone.utc)
            start, end = _prev_month_window(now)
            self.assertEqual(start[:7], end[:7], f"ventana cruza mes: {start} → {end}")
            self.assertTrue(start.endswith("-01T00:00:00Z"))
            self.assertTrue(end.endswith("T23:59:59Z"))


if __name__ == "__main__":
    unittest.main()
