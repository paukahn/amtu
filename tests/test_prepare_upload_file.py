"""_prepare_upload_file: sin FutureWarning de pandas, mismo TSV de siempre
(pase 3e).

Regresión real de producción: un fichero de trackings con una columna
COMPLETAMENTE vacía en todas las filas (p.ej. carrier_code sin rellenar para
todo el lote) hacía que `df.replace(regex=True)` disparase el FutureWarning
"Downcasting behavior in `replace`..." de pandas 2.x en cada ejecución del
cron. No es un fallo, pero ensucia logs/correos. Se confirmó que
`pd.option_context("future.no_silent_downcasting", True)` produce un TSV
BYTE A BYTE idéntico al de antes, así que este test fija ambas cosas: cero
warnings Y contenido sin cambios.
"""

import os
import tempfile
import warnings

import pandas as pd
import unittest

from trackings import _prepare_upload_file


class TestPrepareUploadFileNoWarnings(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.dir.cleanup()

    def test_fully_empty_column_produces_no_future_warning(self):
        # carrier_code vacío en TODAS las filas: el caso real que dispara el
        # FutureWarning de pandas si no se maneja explícitamente.
        df = pd.DataFrame({
            "order_id": ["1", "2"],
            "tracking_number": ["AA123", "BB456"],
            "carrier_code": [pd.NA, pd.NA],
            "ship_date": ["2026-08-01", "2026-08-02"],
        })

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            temp_file = _prepare_upload_file(df, self.dir.name, "cos", "es")

        future_warnings = [w for w in caught if issubclass(w.category, FutureWarning)]
        self.assertEqual(future_warnings, [], f"FutureWarning inesperado: {future_warnings}")

        with open(temp_file, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("order-id\ttracking-number\tcarrier-code\tship-date", content)
        self.assertIn("1\tAA123\t\t2026-08-01", content)  # celda vacía, no "nan"/"NA" literal

    def test_embedded_tab_and_newline_are_still_flattened(self):
        # La regla que motivó el replace() sigue funcionando igual.
        df = pd.DataFrame({
            "order_id": ["1"],
            "tracking_number": ["AA\t123\n456"],
            "carrier_code": ["DHL"],
        })
        temp_file = _prepare_upload_file(df, self.dir.name, "cos", "es")
        with open(temp_file, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("AA 123 456", content)
        self.assertNotIn("AA\t123", content)


if __name__ == "__main__":
    unittest.main()
