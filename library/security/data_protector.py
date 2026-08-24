import hmac
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def pad(data: bytes) -> bytes:
    padding_length = 16 - len(data) % 16
    return data + bytes([padding_length]) * padding_length

def unpad(data: bytes) -> bytes:
    padding_length = data[-1]
    return data[:-padding_length]

def encrypt(data: bytes, key: bytes, hmac_key: bytes):
    padded_data = pad(data)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(padded_data)
    full = iv + cipher_text
    tag = hmac.new(hmac_key, full, sha256).digest()

    return full + tag

def decrypt(path: str, key: bytes, hmac_key: bytes):
    with open(path, "rb") as file:
        data = file.read()

    tag = data[-32:]
    cipher_text = data[:-32]

    expected_tag = hmac.new(hmac_key, cipher_text, sha256).digest()
    if not hmac.compare_digest(tag, expected_tag):
        raise Exception("Invalid signature")

    iv = cipher_text[:16]
    ct = cipher_text[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = cipher.decrypt(ct)
    return unpad(padded_data).decode("utf-8")