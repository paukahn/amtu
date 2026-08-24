"""DataTransformer._apply_logic: format_map SOLO sobre plantillas de config.

Antes se aplicaba format_map a cualquier valor con "{", incluidos los datos
crudos de Amazon (buyer-name, gift-message, direcciones). Un valor como "{Jr}"
tumbaba la transformación (KeyError) y "{x.__class__}" era inyección de
format-string. Ahora los datos pasan literales; solo se expanden las plantillas
declaradas en la config (source=logic y rule.result).
"""

import unittest

from classes.config import DataTransformer


def _make_transformer(sap_columns):
    # client sin mapping -> config vacío; inyectamos sap_columns a mano.
    t = DataTransformer("clientesinmapping", "ES")
    t.sap_columns = sap_columns
    return t


class TestApplyLogicFormatMap(unittest.TestCase):
    def test_amazon_data_with_braces_is_not_formatted(self):
        # Campo de datos (tsv) con sintaxis de plantilla: debe pasar LITERAL.
        cols = [{"name": "BuyerName", "source": "tsv", "amz_name": "buyer-name"}]
        t = _make_transformer(cols)
        row = {"order-id": "111", "buyer-name": "Smith {Jr}"}
        out = t._apply_logic(row, {})
        self.assertEqual(out["BuyerName"], "Smith {Jr}")  # sin crash, sin expandir

    def test_format_string_injection_is_inert(self):
        cols = [{"name": "Gift", "source": "tsv", "amz_name": "gift-message"}]
        t = _make_transformer(cols)
        row = {"order-id": "1", "gift-message": "{order-id.__class__}"}
        out = t._apply_logic(row, {})
        self.assertEqual(out["Gift"], "{order-id.__class__}")  # no se evalúa

    def test_config_logic_template_is_expanded(self):
        cols = [{"name": "Acc", "source": "logic", "value": "{account}"}]
        t = _make_transformer(cols)
        out = t._apply_logic({"order-id": "1"}, {})
        self.assertEqual(out["Acc"], "clientesinmapping")  # plantilla SÍ se expande

    def test_bad_config_template_does_not_crash(self):
        cols = [{"name": "Bad", "source": "logic", "value": "{no_existe}"}]
        t = _make_transformer(cols)
        out = t._apply_logic({"order-id": "1"}, {})
        self.assertEqual(out["Bad"], "{no_existe}")  # se deja literal, sin excepción


if __name__ == "__main__":
    unittest.main()
