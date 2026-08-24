"""Utilidades pequeñas y genéricas (gzip + confirmación CLI).

Adelgazado en el pase 2: este módulo era un cajón de sastre con siete
responsabilidades. Lo que vivía aquí se movió a su sitio:

- metadatos de países (currency/region/locale)   -> library.marketplaces
- correo (send_mail / notify_error_mail)         -> library.mailer
- feed de stock (stock_json_convert)             -> library.stock_feed
- brand analytics (convert_json, decipher_json,
  divide_asins_in_blocks)                        -> eliminados con el módulo
- download_and_unzip (requests SIN timeout)      -> client.download_bytes + gunzip_to_text
- get_acronym / gzip_json_data / is_valid_gzip   -> eliminados (sin llamadores)
"""

from __future__ import annotations

import gzip
from io import BytesIO


def gunzip_to_text(data: bytes, encoding: str = "utf-8") -> str:
    """Descomprime un blob gzip a texto."""
    with gzip.GzipFile(fileobj=BytesIO(data)) as f:
        return f.read().decode(encoding)


def confirm(prompt):
    return input(f"{prompt} (s/n): ").strip().lower() == "s"


def mask_secret(value: str, keep: int = 4) -> str:
    """Representación segura de un secreto para prompts/listados de la CLI:
    solo los últimos `keep` caracteres. El valor completo queda reservado a
    los volcados explícitos protegidos por confirm()."""
    if not value:
        return ""
    if len(value) <= keep:
        return "…" * len(value)
    return f"…{value[-keep:]}"
