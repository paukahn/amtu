"""Match de fichero de trackings por acrónimo, sin distinguir mayúsculas.

Regresión real en producción: acronyms.txt = "cosmic = COS" (mayúsculas) pero los
ficheros llegan como "cos_uk_trackings_output.txt" (minúsculas). Con el match
sensible a mayúsculas el fichero se descartaba en silencio y trackings terminaba
sin procesar nada.
"""

import unittest

from trackings import _belongs_to_acronym


class TestBelongsToAcronym(unittest.TestCase):
    def test_lowercase_file_uppercase_acronym(self):
        # El caso real del bug.
        self.assertTrue(_belongs_to_acronym("cos_uk_trackings_output.txt", "COS"))

    def test_uppercase_file_uppercase_acronym(self):
        self.assertTrue(_belongs_to_acronym("COS_UK_trackings_output.txt", "COS"))

    def test_lowercase_acronym_too(self):
        self.assertTrue(_belongs_to_acronym("cos_uk_x.txt", "cos"))

    def test_does_not_match_other_account(self):
        self.assertFalse(_belongs_to_acronym("abc_uk_x.txt", "COS"))

    def test_requires_underscore_separator(self):
        # "cosmic_..." NO debe colar como prefijo "cos" (evita falsos positivos).
        self.assertFalse(_belongs_to_acronym("cosmic_uk_x.txt", "COS"))


if __name__ == "__main__":
    unittest.main()
