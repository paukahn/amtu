"""DataTransformer.transform: guard de mapping vacío + escritura atómica (pase 3).

Regresión (alta): sin reglas para el país (mapping ausente o país fuera de
country_rules/groups) sap_columns quedaba [] y transform() escribía un fichero
de filas VACÍAS devolviendo True — orders lo daba por bueno y lo enviaba a
SAP/FTP como una exportación «exitosa».
"""

import os
import tempfile
import unittest

from classes.config import DataTransformer


def _make_transformer(sap_columns):
    t = DataTransformer("clientesinmapping", "ES")
    t.sap_columns = sap_columns
    return t


RAW_TSV = "order-id\tbuyer-name\n111-1234567-1234567\tSmith\n"


class TestTransformGuard(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.raw = os.path.join(self.dir.name, "raw.tsv")
        with open(self.raw, "w", encoding="utf-8") as f:
            f.write(RAW_TSV)
        self.out = os.path.join(self.dir.name, "out.txt")

    def tearDown(self):
        self.dir.cleanup()

    def test_empty_sap_columns_returns_false_and_writes_nothing(self):
        t = _make_transformer([])
        self.assertFalse(t.transform(self.raw, self.out, xml_info={}))
        self.assertFalse(os.path.exists(self.out))

    def test_valid_mapping_writes_file_and_returns_true(self):
        cols = [{"name": "Pedido", "source": "tsv", "amz_name": "order-id"}]
        t = _make_transformer(cols)
        self.assertTrue(t.transform(self.raw, self.out, xml_info={}))
        with open(self.out, encoding="utf-8", newline="") as f:
            content = f.read()
        self.assertEqual(content, "Pedido\r\n111-1234567-1234567\r\n")

    def test_embedded_tabs_and_newlines_are_flattened(self):
        # El consumidor corta por '\t' sin parser CSV: un tab embebido
        # descuadraría columnas; se aplana a espacio.
        raw2 = os.path.join(self.dir.name, "raw2.tsv")
        with open(raw2, "w", encoding="utf-8") as f:
            f.write("order-id\tgift-message\n111-1234567-1234567\thola\n")
        cols = [
            {"name": "Pedido", "source": "tsv", "amz_name": "order-id"},
            {"name": "Nota", "source": "logic", "value": "linea1\nlinea2\tcol"},
        ]
        t = _make_transformer(cols)
        self.assertTrue(t.transform(raw2, self.out, xml_info={}))
        with open(self.out, encoding="utf-8", newline="") as f:
            lines = f.read().split("\r\n")
        self.assertEqual(lines[1], "111-1234567-1234567\tlinea1 linea2 col")

    def test_no_temp_leftovers_in_output_dir(self):
        cols = [{"name": "Pedido", "source": "tsv", "amz_name": "order-id"}]
        t = _make_transformer(cols)
        t.transform(self.raw, self.out, xml_info={})
        leftovers = [n for n in os.listdir(self.dir.name) if n.endswith(".tmp")]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
