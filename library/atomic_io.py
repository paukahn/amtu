"""Escritura atómica de ficheros (pase 3).

Los almacenes cifrados (tokens.amztok, applications.amzapps, …) son un blob
AES-CBC+HMAC: NO existe un estado «parcialmente válido». Una escritura
interrumpida (caída del proceso, disco lleno, corte de luz) dejaba el HMAC
inválido y se perdían TODOS los refresh-tokens sin copia de respaldo.

Patrón: escribir a un temporal en el MISMO directorio (evita EXDEV si el
destino está en otro sistema de ficheros/montaje) y publicar con os.replace,
que es atómico en POSIX y en NTFS. Con backup=True se conserva la versión
anterior en <path>.bak (restauración manual si el fichero nuevo resultara
inválido). Mismo patrón que ya usaba auth_provider._write_cache.
"""

from __future__ import annotations

import os
import shutil


def atomic_write_bytes(path: str, data: bytes, *, backup: bool = False) -> None:
    """Escribe `data` en `path` de forma atómica (temp en el mismo dir + os.replace)."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    tmp = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        if backup and os.path.exists(path):
            # copy2 (no move): si el replace de abajo fallara, `path` sigue intacto.
            shutil.copy2(path, path + ".bak")
        os.replace(tmp, path)
    finally:
        # Limpieza del temporal si algo falló antes del replace.
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def atomic_write_text(path: str, text: str, *, encoding: str = "utf-8",
                      newline: str = "", backup: bool = False) -> None:
    """Variante de texto. `newline=""` conserva los saltos tal cual se pasan."""
    data = text.encode(encoding)
    if newline:
        data = text.replace("\n", newline).encode(encoding)
    atomic_write_bytes(path, data, backup=backup)
