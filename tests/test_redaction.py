"""Redacción de secretos en el log de debug del transporte.

El cuerpo de respuesta de la SP-API puede contener el restrictedDataToken y
URLs pre-firmadas de S3 (acceso directo al documento, a menudo con PII). El
volcado de debug debe redactarlos; antes solo se redactaban las cabeceras.
"""

import unittest

from library.transport import _redact_body


class TestRedactBody(unittest.TestCase):
    def test_redacts_restricted_data_token(self):
        body = '{"restrictedDataToken":"Atza|RDT-SECRET-VALUE","expiresIn":3600}'
        out = _redact_body(body)
        self.assertNotIn("Atza|RDT-SECRET-VALUE", out)
        self.assertIn('"restrictedDataToken":"***"', out)
        self.assertIn("expiresIn", out)  # lo no sensible se conserva

    def test_redacts_presigned_url(self):
        body = '{"url":"https://tortuga-prod.s3.amazonaws.com/doc?X-Amz-Signature=abc","feedDocumentId":"FD1"}'
        out = _redact_body(body)
        self.assertNotIn("X-Amz-Signature", out)
        self.assertIn('"url":"***"', out)
        self.assertIn("FD1", out)

    def test_handles_spaces_around_colon(self):
        body = '{"url" : "https://secret-url"}'
        out = _redact_body(body)
        self.assertNotIn("secret-url", out)

    def test_non_sensitive_body_unchanged(self):
        body = '{"reportId":"R1","processingStatus":"DONE"}'
        self.assertEqual(_redact_body(body), body)


if __name__ == "__main__":
    unittest.main()
