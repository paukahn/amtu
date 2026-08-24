"""load_trackings: números de tracking SIEMPRE como texto (pase 3).

Regresión: el dtype anterior apuntaba a la columna "order-id", que en el
fichero de la ERP aún se llama "order_id" (el rename ocurre después, en
trackings). pandas infería tipos: los trackings de 20 dígitos desbordaban
int64 a float64 y salían como '1.2e+19', y los ceros a la izquierda se
perdían — a Amazon llegaban números de seguimiento corruptos.
"""

import os
import tempfile
import unittest

from library.file_explorer import load_trackings


class TestLoadTrackingsTypes(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.dir.cleanup()

    def _write(self, name, content, encoding="utf-8"):
        path = os.path.join(self.dir.name, name)
        with open(path, "w", encoding=encoding, newline="") as f:
            f.write(content)
        return name

    def test_long_tracking_numbers_survive_as_strings(self):
        fname = self._write(
            "cos_es_trackings_output.txt",
            "order_id\ttracking_number\tcarrier_code\tship_date\n"
            "028-1234567-1234567\t00340434161094042557\tDHL\t2026-06-01\n",
        )
        df = load_trackings("cuenta", "es", self.dir.name, filename=fname)
        self.assertIsNotNone(df)
        value = df["tracking_number"].iloc[0]
        self.assertIsInstance(value, str)
        self.assertEqual(value, "00340434161094042557")  # 20 dígitos, ceros intactos

    def test_order_id_is_string(self):
        fname = self._write(
            "cos_es_trackings_output.txt",
            "order_id\ttracking_number\n123\t456\n",
        )
        df = load_trackings("cuenta", "es", self.dir.name, filename=fname)
        self.assertEqual(df["order_id"].iloc[0], "123")

    def test_cp1252_file_is_not_skipped(self):
        # Un byte no-utf8 (ñ en cp1252) antes hacía descartar el fichero entero.
        fname = self._write(
            "cos_es_trackings_output.txt",
            "order_id\ttracking_number\tcarrier_code\n1\t2\tCorreos España\n",
            encoding="cp1252",
        )
        df = load_trackings("cuenta", "es", self.dir.name, filename=fname)
        self.assertIsNotNone(df)
        self.assertEqual(df["carrier_code"].iloc[0], "Correos España")


if __name__ == "__main__":
    unittest.main()
