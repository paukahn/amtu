"""Tests del parser base de configuración (classes/config/base.py)."""

import os
import tempfile
import unittest

from classes.config.base import ConfigError, parse_flat, parse_sections, read_config_text, save_sections


class TestParseSections(unittest.TestCase):
    def test_basic_sections_and_pairs(self):
        text = "[cuenta]\nmercados = eu, na\naplicacion = MiApp\n"
        sections = parse_sections(text)
        self.assertEqual(list(sections), ["cuenta"])
        self.assertEqual(sections["cuenta"], [("mercados", "eu, na"), ("aplicacion", "MiApp")])

    def test_duplicate_keys_are_preserved_in_order(self):
        # Las clases deciden el plegado: accounts acumula, stock primero, tokens último.
        text = "[a]\nmercados = eu\nmercados = na\n"
        sections = parse_sections(text)
        self.assertEqual(sections["a"], [("mercados", "eu"), ("mercados", "na")])

    def test_duplicate_sections_are_merged(self):
        text = "[a]\nx = 1\n[b]\ny = 2\n[a]\nz = 3\n"
        sections = parse_sections(text)
        self.assertEqual(sections["a"], [("x", "1"), ("z", "3")])

    def test_block_comments_toggle(self):
        text = "'''\n[fantasma]\nx = 1\n'''\n[real]\ny = 2\n"
        sections = parse_sections(text, block_comments=True)
        self.assertEqual(list(sections), ["real"])

    def test_inline_comments_stripped_when_enabled(self):
        text = "[a]\nx = 1  # comentario\n"
        sections = parse_sections(text, inline_comments=True)
        self.assertEqual(sections["a"], [("x", "1")])

    def test_hash_preserved_in_values_when_inline_disabled(self):
        # Crítico para ficheros cifrados: contraseñas/secretos con '#'.
        text = "[a]\npassword = se#creto\n"
        sections = parse_sections(text)
        self.assertEqual(sections["a"], [("password", "se#creto")])

    def test_full_line_comment_skipped_when_inline_disabled(self):
        text = "# cabecera\n[a]\nx = 1\n"
        sections = parse_sections(text)
        self.assertEqual(sections["a"], [("x", "1")])

    def test_malformed_line_reported_and_skipped(self):
        warnings = []
        text = "[a]\nsin_igual\nx = 1\n"
        sections = parse_sections(text, on_warning=warnings.append)
        self.assertEqual(sections["a"], [("x", "1")])
        self.assertEqual(len(warnings), 1)

    def test_section_names_keep_original_case(self):
        text = "[MiApp]\nx = 1\n"
        sections = parse_sections(text)
        self.assertEqual(list(sections), ["MiApp"])


class TestParseFlat(unittest.TestCase):
    def test_pairs_and_comments(self):
        text = "# comentario\n; otro\nreports_folder = out\nmode=debug\nbasura\n"
        warnings = []
        pairs = parse_flat(text, on_warning=warnings.append)
        self.assertEqual(pairs, [("reports_folder", "out"), ("mode", "debug")])
        self.assertEqual(len(warnings), 1)


class TestSaveSections(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "out.ini")

    def tearDown(self):
        self.dir.cleanup()

    def _read(self):
        with open(self.path, encoding="utf-8") as f:
            return f.read()

    def test_default_filters_empty_values_and_sections(self):
        # Comportamiento Tokens/FTP: valores vacíos y secciones vacías fuera.
        save_sections(self.path, {"a": {"x": "1", "y": ""}, "b": {"z": None}})
        self.assertEqual(self._read(), "[a]\nx = 1\n")

    def test_keep_empty_preserves_blank_fields(self):
        # Comportamiento Applications: el save antiguo escribía campos vacíos.
        save_sections(self.path, {"a": {"x": "1", "y": "", "enabled": False}}, keep_empty=True)
        self.assertEqual(self._read(), "[a]\nx = 1\ny = \nenabled = false\n")


class TestReadConfigText(unittest.TestCase):
    def test_missing_file_raises_config_error(self):
        with self.assertRaises(ConfigError):
            read_config_text(os.path.join(tempfile.gettempdir(), "no_existe_xyz.ini"))

    def test_reads_plain_text(self):
        with tempfile.NamedTemporaryFile("w", suffix=".ini", delete=False, encoding="utf-8") as f:
            f.write("[a]\nx = 1\n")
            path = f.name
        try:
            self.assertIn("[a]", read_config_text(path))
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
