"""Carga de las llaves maestras (key + hmac_key, 32 bytes cada una).

Pase 3 — endurecido para el despliegue real (servidor Linux + cron):

Orden de búsqueda en modo automático (auto=True):
1. Variable de entorno AMTUBB_MASTER_KEYS: base64 de los 64 bytes crudos.
   Permite sacar el material de clave del árbol del proyecto por completo
   (p.ej. `EnvironmentFile` de systemd o un `. /etc/amtubb/keys.env` en la
   línea de cron con permisos 0600 y dueño root:svc).
2. Fichero apuntado por AMTUBB_KEYS_FILE (ruta absoluta recomendada, fuera
   del directorio del proyecto y de sus backups).
3. `.env.secret` en el directorio de trabajo (compatibilidad).

Permisos en POSIX: el chequeo es SOLO INFORMATIVO (decisión registrada en
REFACTORING.md §7): si el fichero de llaves es legible por CUALQUIER usuario
(bits 0o007) se emite un warning en el log con el chmod recomendado, pero
NUNCA se falla ni se hace chmod automático — la carga de llaves no puede
romperse por permisos en ningún escenario (cron sin privilegios, montajes
NFS/vfat donde chmod no aplica, propietario distinto del usuario del cron…).
La lectura por grupo (0640) es la forma normal de dar acceso al cron y no
genera ni siquiera warning. En Windows no hay chequeo (los ACL de NTFS no se
mapean a bits POSIX).

El modo interactivo (auto=False) sigue igual: contraseña + secret_keys.bin
(PBKDF2-SHA256/600k + AES-CBC + HMAC, ver crypto_utils).
"""

import base64
import os
import getpass
import stat

from .crypto_utils import load_keys as load_encrypted_keys

SECRET_ENV = ".env.secret"
SECRET_BIN = "secret_keys.bin"
ENV_KEYS_VAR = "AMTUBB_MASTER_KEYS"
ENV_FILE_VAR = "AMTUBB_KEYS_FILE"
KEY_BYTES = 64  # key[32] + hmac_key[32]


def _split(content: bytes):
    if len(content) != KEY_BYTES:
        raise ValueError(
            f"material de llaves de tamaño incorrecto ({len(content)} bytes), deberían ser {KEY_BYTES}"
        )
    return content[:32], content[32:]


def _is_world_readable(mode: int) -> bool:
    """True si los bits de OTROS dan algún acceso (0o007)."""
    return bool(mode & 0o007)


def _warn_if_world_readable(path: str) -> None:
    """POSIX: warning (y solo warning) si las llaves son legibles por todos.

    No falla nunca ni intenta chmod: correr es más importante que el aviso, y
    un chmod automático desde una ejecución manual del propietario podría
    romper el acceso del usuario del cron."""
    if os.name != "posix":
        return
    try:
        mode = stat.S_IMODE(os.stat(path).st_mode)
    except OSError:
        return
    if not _is_world_readable(mode):
        return
    msg = (
        f"⚠️ '{path}' es legible por CUALQUIER usuario del sistema ({oct(mode)}). "
        f"Recomendado: chmod o-rwx {path} — el acceso por grupo basta para el cron."
    )
    try:
        from library.logging_helpers import error
        error(msg, type="warning")
    except Exception:
        print(msg)


def _load_auto():
    # 1) Variable de entorno con el material en base64.
    env_value = os.environ.get(ENV_KEYS_VAR)
    if env_value:
        try:
            return _split(base64.b64decode(env_value, validate=True))
        except Exception as e:
            raise RuntimeError(f"{ENV_KEYS_VAR} no contiene base64 válido de {KEY_BYTES} bytes: {e}") from e

    # 2) Fichero externo señalado por variable de entorno; 3) .env.secret local.
    path = os.environ.get(ENV_FILE_VAR) or SECRET_ENV
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"No se encontró el fichero de llaves '{path}' "
            f"(defínelo con {ENV_FILE_VAR} o crea {SECRET_ENV} con app_control)."
        )
    _warn_if_world_readable(path)
    with open(path, "rb") as f:
        return _split(f.read())


def load_keys(auto=False):
    """
    Devuelve (key, hmac_key).

    - auto=True  → entorno/fichero de llaves sin contraseña (para cron).
    - auto=False → pide contraseña y usa secret_keys.bin.
    """
    if auto:
        try:
            return _load_auto()
        except Exception as e:
            raise RuntimeError(f"No se pudieron cargar las llaves automáticamente: {e}") from e

    if not os.path.exists(SECRET_BIN):
        raise FileNotFoundError("No existe secret_keys.bin, inicialízalo con CLI primero.")

    password = getpass.getpass("Introduce contraseña maestra: ")
    return load_encrypted_keys(password)


def load_master_keys():
    try:
        return load_keys(auto=True)
    except Exception as e:
        raise RuntimeError(f"❌ No se pudieron cargar las llaves automáticamente: {e}") from e
