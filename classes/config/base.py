"""Base compartida del paquete de configuración (pase 2 del refactor).

Sustituye los nueve parsers INI manuales casi idénticos (uno por clase) por un
único parser y un único contrato de errores:

- `ConfigError` en lugar de `print(...) + sys.exit(1)`. El código de librería
  ya no puede matar el proceso: el runner aísla el fallo por cuenta y la CLI
  lo muestra como mensaje. (Antes el runner tenía que capturar `SystemExit`.)
- `parse_sections` entiende el dialecto usado por los ficheros del proyecto:
  secciones `[nombre]`, `clave = valor`, comentarios `#` y bloques
  '''...''' / \"\"\"...\"\"\" (accounts.ini, stock.ini). Devuelve los pares
  clave/valor EN ORDEN y CON duplicados, porque las clases los pliegan con
  reglas distintas (accounts acumula listas, stock se queda con el primero,
  tokens con el último).
- `parse_flat` para ficheros sin secciones (common.ini, acronyms.txt, mail).
- `read_config_text` resuelve la ruta y descifra si se pasan llaves.

OJO con `inline_comments`: solo debe activarse en ficheros de texto plano
(accounts/stock/polling). En los ficheros cifrados hay contraseñas y secretos
que pueden contener '#'; ahí los comentarios solo valen a línea completa.
"""

from __future__ import annotations

import os
import sys


class ConfigError(Exception):
    """Configuración ausente, ilegible o inválida."""


def warn_print(message: str) -> None:
    """print() tolerante a consolas no-UTF8 (cp1252 en Windows).

    Los avisos interpolan CONTENIDO del fichero de config (utf-8): un carácter
    no representable en la consola lanzaba UnicodeEncodeError y tumbaba la
    CARGA del config en vez de avisar. Un warning jamás debe romper nada."""
    try:
        print(message)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(message.encode(enc, errors="replace").decode(enc, errors="replace"))


def config_path(directory: str, filename: str) -> str:
    return os.path.join(os.getcwd(), directory or "", filename)


def read_config_text(path: str, key: bytes | None = None, hmac_key: bytes | None = None) -> str:
    """Lee el fichero como texto; si hay llaves, lo descifra antes."""
    if not os.path.exists(path):
        raise ConfigError(f"No se encuentra el archivo '{os.path.basename(path)}' ({path}).")
    if key and hmac_key:
        from library.security.data_protector import decrypt
        try:
            return decrypt(path, key, hmac_key)
        except Exception as e:
            raise ConfigError(f"No se pudo descifrar '{os.path.basename(path)}': {e}") from e
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError as e:
        # Un blob AES leído como utf-8: el llamador olvidó pasar las llaves.
        raise ConfigError(
            f"'{os.path.basename(path)}' parece cifrado y no se pasaron llaves para descifrarlo."
        ) from e


def parse_sections(
    text: str,
    *,
    inline_comments: bool = False,
    block_comments: bool = False,
    on_warning=warn_print,
) -> dict[str, list[tuple[str, str]]]:
    """Parsea texto tipo INI a {sección: [(clave, valor), ...]}.

    - Los nombres de sección conservan su caso original; las clases deciden
      si normalizan a minúsculas.
    - Secciones repetidas se fusionan (los pares se acumulan), igual que en
      los parsers antiguos.
    - Líneas malformadas se reportan vía `on_warning` y se ignoran.
    """
    sections: dict[str, list[tuple[str, str]]] = {}
    current: str | None = None
    in_block = False

    for idx, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue

        if block_comments and line.startswith(("'''", '"""')):
            in_block = not in_block
            continue
        if in_block:
            continue

        if inline_comments:
            if "#" in line:
                line = line.split("#")[0].strip()
        elif line.startswith("#"):
            continue
        if not line:
            continue

        if line.startswith("[") and line.endswith("]"):
            name = line[1:-1].strip()
            if not name:
                on_warning(f"Línea {idx}: nombre de sección vacío.")
                current = None
                continue
            current = name
            sections.setdefault(current, [])
            continue

        if "=" in line and current is not None:
            key, value = line.split("=", 1)
            sections[current].append((key.strip(), value.strip()))
        else:
            on_warning(f"Línea {idx}: línea malformada o fuera de sección -> '{raw.strip()}'")

    return sections


def parse_flat(text: str, *, on_warning=warn_print) -> list[tuple[str, str]]:
    """Parsea `clave = valor` por línea, sin secciones. '#'/';' a línea completa."""
    pairs: list[tuple[str, str]] = []
    for idx, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith(("#", ";")):
            continue
        if "=" not in line:
            on_warning(f"Línea {idx} ignorada: '{line}'")
            continue
        key, value = line.split("=", 1)
        pairs.append((key.strip(), value.strip()))
    return pairs


# Extensiones de los almacenes de secretos: guardarlos SIN llaves los dejaría
# en texto plano en disco. Se rechaza en save_sections (pase 3).
SECRET_SUFFIXES = (".amztok", ".amzapps", ".amzaccs", ".email")


def save_sections(path: str, sections: dict[str, dict[str, object]],
                  key: bytes | None = None, hmac_key: bytes | None = None,
                  *, keep_empty: bool = False) -> None:
    """Serializa {sección: {clave: valor}} al formato `[sección]` / `k = v`.

    Mantiene el formato exacto que escribían los `save()` antiguos (espacios
    alrededor del '=', línea en blanco entre secciones). Por defecto omite
    valores vacíos y secciones vacías (comportamiento de Tokens/FTP);
    `keep_empty=True` los conserva (comportamiento de Applications, cuyo save
    antiguo escribía también los campos vacíos). Cifra si se pasan llaves.

    Pase 3: escritura ATÓMICA (temp + os.replace) con copia previa en .bak.
    El fichero cifrado no tiene estados intermedios válidos: una escritura
    parcial rompía el HMAC y perdía todos los tokens sin copia de respaldo.
    """
    if path.endswith(SECRET_SUFFIXES) and not (key and hmac_key):
        raise ConfigError(
            f"'{os.path.basename(path)}' es un almacén de secretos: guardarlo sin llaves "
            "lo dejaría en texto plano. Pasa key/hmac_key."
        )

    lines: list[str] = []
    for name, data in sections.items():
        if keep_empty:
            items = {k: ("" if v is None else v) for k, v in data.items()}
        else:
            items = {k: v for k, v in data.items() if v is not None and str(v).strip() != ""}
            if not items:
                continue
        lines.append(f"[{name}]")
        for k, v in items.items():
            val = str(v).lower() if isinstance(v, bool) else str(v)
            lines.append(f"{k} = {val}")
        lines.append("")

    full_text = "\n".join(lines).strip() + "\n"

    from library.atomic_io import atomic_write_bytes
    try:
        if key and hmac_key:
            from library.security.data_protector import encrypt
            payload = encrypt(full_text.encode("utf-8"), key, hmac_key)
        else:
            payload = full_text.encode("utf-8")
        atomic_write_bytes(path, payload, backup=True)
    except OSError as e:
        raise ConfigError(f"No se pudo guardar '{os.path.basename(path)}': {e}") from e
