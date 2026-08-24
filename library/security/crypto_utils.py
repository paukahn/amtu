"""Cifrado de la llave maestra en secret_keys.bin (ruta CLI con contraseña).

Formato v2 (nuevo): byte-versión(0x02) + salt(16) + iv(16) + ciphertext + tag-HMAC(32).
- KDF: PBKDF2-HMAC-SHA256, 600k iteraciones (antes: HMAC-SHA1, 100k).
- Encrypt-then-MAC: deriva 64 bytes (enc[:32] + mac[32:]); el tag HMAC-SHA256
  cubre versión+salt+iv+ciphertext y se verifica con compare_digest ANTES de
  descifrar. Antes el formato AES-CBC no tenía autenticación (solo len==64).

Compatibilidad: `load_keys` lee también el formato v1 antiguo (sin byte-versión,
SHA1/100k, sin HMAC). Migración automática: el siguiente `encrypt_keys`
(p.ej. al cambiar credenciales por CLI) reescribe en v2. La ruta de cron
(.env.secret, 64 bytes crudos) NO usa este módulo y queda igual.
"""

import hmac
from hashlib import sha256

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

KEY_FILE = "secret_keys.bin"
SALT_SIZE = 16
VERSION_V2 = 0x02
ITERATIONS_V2 = 600_000
ITERATIONS_V1 = 100_000  # legacy, solo para leer ficheros antiguos


def pad(data: bytes) -> bytes:
    padding_len = 16 - len(data) % 16
    return data + bytes([padding_len]) * padding_len


def unpad(data: bytes) -> bytes:
    padding_len = data[-1]
    return data[:-padding_len]


def _derive_v2(password: str, salt: bytes):
    dk = PBKDF2(password, salt, dkLen=64, count=ITERATIONS_V2, hmac_hash_module=SHA256)
    return dk[:32], dk[32:]  # (enc_key, mac_key)


def _derive_v1(password: str, salt: bytes) -> bytes:
    # PBKDF2 por defecto = HMAC-SHA1 (formato antiguo).
    return PBKDF2(password, salt, dkLen=32, count=ITERATIONS_V1)


def encrypt_keys(key: bytes, hmac_key: bytes, password: str):
    salt = get_random_bytes(SALT_SIZE)
    enc_key, mac_key = _derive_v2(password, salt)

    cipher = AES.new(enc_key, AES.MODE_CBC)
    iv = cipher.iv
    ciphertext = cipher.encrypt(pad(key + hmac_key))

    head = bytes([VERSION_V2]) + salt + iv + ciphertext
    tag = hmac.new(mac_key, head, sha256).digest()

    # Atómico: perder secret_keys.bin a media escritura dejaría la ruta CLI
    # sin llaves maestras (la de cron sobrevive vía .env.secret).
    from library.atomic_io import atomic_write_bytes
    atomic_write_bytes(KEY_FILE, head + tag, backup=True)


def _load_v2(content: bytes, password: str):
    if len(content) < 1 + SALT_SIZE + 16 + 16 + 32:
        raise ValueError("Fichero v2 demasiado corto.")
    head, tag = content[:-32], content[-32:]
    salt = head[1:1 + SALT_SIZE]
    iv = head[1 + SALT_SIZE:1 + SALT_SIZE + 16]
    ciphertext = head[1 + SALT_SIZE + 16:]

    enc_key, mac_key = _derive_v2(password, salt)
    expected = hmac.new(mac_key, head, sha256).digest()
    if not hmac.compare_digest(tag, expected):
        raise ValueError("Firma inválida o contraseña incorrecta.")

    data = unpad(AES.new(enc_key, AES.MODE_CBC, iv).decrypt(ciphertext))
    if len(data) != 64:
        raise ValueError("Datos corruptos.")
    return data[:32], data[32:]


def _load_v1(content: bytes, password: str):
    salt = content[:SALT_SIZE]
    iv = content[SALT_SIZE:SALT_SIZE + 16]
    ciphertext = content[SALT_SIZE + 16:]
    data = unpad(AES.new(_derive_v1(password, salt), AES.MODE_CBC, iv).decrypt(ciphertext))
    if len(data) != 64:
        raise ValueError("Datos corruptos o contraseña incorrecta.")
    return data[:32], data[32:]


# Longitudes EXACTAS de cada formato para el payload fijo de 64 bytes
# (key+hmac_key -> pad PKCS7 a 80 bytes de ciphertext):
# v1: salt(16)+iv(16)+ct(80)            = 112
# v2: ver(1)+salt(16)+iv(16)+ct(80)+mac(32) = 145
_V1_LEN = 112
_V2_LEN = 145


def load_keys(password: str):
    """Devuelve (key, hmac_key). Lee v2 (autenticado) y, por compatibilidad, v1.

    Pase 3: el formato se decide por la LONGITUD del fichero (112 = v1,
    145 = v2), que es inequívoca para este payload fijo — mejor que el byte de
    versión: un v1 cuya sal empezara casualmente por 0x02 ya no puede caer en
    la rama equivocada, y un MAC inválido en v2 (contraseña incorrecta) da su
    error real en vez de degradar en silencio a la ruta v1 sin autenticación.
    """
    with open(KEY_FILE, "rb") as f:
        content = f.read()

    if len(content) == _V1_LEN:
        return _load_v1(content, password)
    if len(content) == _V2_LEN and content[:1] == bytes([VERSION_V2]):
        return _load_v2(content, password)
    raise ValueError(
        f"'{KEY_FILE}' no tiene un formato reconocible ({len(content)} bytes): "
        "ni v1 (112) ni v2 (145). ¿Fichero corrupto? Restaura desde .bak."
    )
