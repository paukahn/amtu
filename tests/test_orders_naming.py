"""Nombre del fichero de pedidos y ventana de fechas (pase 3b).

Nombre: MINÚSCULAS ('..._cos_amz.txt') — decisión CONFIRMADA por el operador.
Los ficheros históricos en mayúsculas ('..._COS_AMZ.txt') de la versión
síncrona eran el defecto, no la referencia.

Ventana: 7 días hasta «ahora» — decisión CONFIRMADA por el operador (los 14
días de la versión síncrona antigua eran demasiado).
"""

import unittest
from datetime import datetime, timezone

from orders import _local_output_name, _orders_date_range


class TestLocalOutputName(unittest.TestCase):
    def test_acronym_and_amz_lowercased(self):
        # Confirmado por el operador: el consumidor espera minúsculas.
        self.assertEqual(
            _local_output_name("320655020622", "COS", "txt"),
            "320655020622_cos_amz.txt",
        )

    def test_already_lowercase_acronym(self):
        self.assertEqual(_local_output_name("999", "cos", "csv"), "999_cos_amz.csv")

    def test_format_preserved(self):
        self.assertTrue(_local_output_name("1", "ABC", "csv").endswith("_abc_amz.csv"))


class TestOrdersDateRange(unittest.TestCase):
    def test_window_is_7_days_ending_now(self):
        now = datetime(2026, 6, 18, 12, 30, 45, tzinfo=timezone.utc)
        start, end = _orders_date_range(now)
        # end = momento actual exacto; start = 00:00 de hace 7 días.
        self.assertEqual(end, "2026-06-18T12:30:45Z")
        self.assertEqual(start, "2026-06-11T00:00:00Z")

    def test_year_boundary(self):
        now = datetime(2026, 1, 1, 23, 59, 59, tzinfo=timezone.utc)
        start, end = _orders_date_range(now)
        self.assertTrue(start.endswith("T00:00:00Z"))
        self.assertEqual(start, "2025-12-25T00:00:00Z")  # cruza fin de año, 7 días atrás


if __name__ == "__main__":
    unittest.main()
