"""Golden test: el fichero para SAP es BYTE a BYTE el mismo que en pase 2.

Hay clientes con un SAP que reacciona a cada coma de más, así que el pase 3
cambió la mecánica de escritura (atómica, sin csv.DictWriter) con el contrato
de NO cambiar ni un byte del formato para datos normales. Este test lo fija:
escribe las mismas filas con el writer ANTIGUO (csv.DictWriter, QUOTE_MINIMAL,
lineterminator \r\n por defecto) y con DataTransformer.transform, y compara
los bytes.

Única divergencia deliberada (cubierta en test_transform_guard): valores con
tab/salto de línea/comilla embebidos — el writer antiguo los envolvía en
comillas CSV (que un consumidor plano que corta por '\t' NO interpreta y
descuadraba columnas); ahora se aplanan a espacio y el fichero sigue siendo
TSV plano válido.
"""

import csv
import os
import tempfile
import unittest

from classes.config import DataTransformer

# Filas realistas de un export de pedidos (sin caracteres especiales: el caso
# del 99.9% de los datos reales).
SAP_COLUMNS = [
    {"name": "Pedido", "source": "tsv", "amz_name": "order-id"},
    {"name": "Fecha", "source": "tsv", "amz_name": "purchase-date"},
    {"name": "SKU", "source": "tsv", "amz_name": "sku"},
    {"name": "Cantidad", "source": "tsv", "amz_name": "quantity-purchased"},
    {"name": "Precio", "source": "tsv", "amz_name": "item-price"},
    {"name": "Comprador", "source": "tsv", "amz_name": "buyer-name"},
    {"name": "Vacio", "source": "tsv", "amz_name": "no-existe"},
]

RAW_HEADER = "order-id\tpurchase-date\tsku\tquantity-purchased\titem-price\tbuyer-name"
RAW_ROWS = [
    "111-1234567-1234567\t2026-06-28T10:15:00+00:00\tSKU-001\t2\t49,90\tJosé García Pérez",
    "112-7654321-7654321\t2026-06-29T08:00:00+00:00\tSKU-002\t1\t129,00\tMarie-Claire O'Neill",
    "113-1111111-2222222\t2026-06-30T21:45:10+00:00\tSKU-003\t10\t9,99\tМария Иванова",
]


def _old_writer_output(rows, headers):
    """Reproducción exacta del writer del pase 2 (csv.DictWriter)."""
    import io
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=headers, delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


class TestSapFormatCompat(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.raw = os.path.join(self.dir.name, "raw.tsv")
        with open(self.raw, "w", encoding="utf-8") as f:
            f.write(RAW_HEADER + "\n" + "\n".join(RAW_ROWS) + "\n")
        self.out = os.path.join(self.dir.name, "out.txt")

    def tearDown(self):
        self.dir.cleanup()

    def test_output_is_byte_identical_to_pase2_writer(self):
        t = DataTransformer("clientesinmapping", "ES")
        t.sap_columns = SAP_COLUMNS
        self.assertTrue(t.transform(self.raw, self.out, xml_info={}))

        with open(self.out, "rb") as f:
            new_bytes = f.read()

        # Mismo pipeline de filas que transform() para alimentar al writer viejo.
        with open(self.raw, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
            rows = [t._apply_logic({k.strip(): v for k, v in r.items()}, {}) for r in reader]
        headers = [c["name"] for c in SAP_COLUMNS]
        old_bytes = _old_writer_output(rows, headers).encode("utf-8")

        self.assertEqual(new_bytes, old_bytes)

    def test_crlf_line_endings_preserved(self):
        t = DataTransformer("clientesinmapping", "ES")
        t.sap_columns = SAP_COLUMNS
        t.transform(self.raw, self.out, xml_info={})
        with open(self.out, "rb") as f:
            data = f.read()
        self.assertEqual(data.count(b"\r\n"), 4)  # cabecera + 3 filas
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))  # ningún LF suelto


if __name__ == "__main__":
    unittest.main()
