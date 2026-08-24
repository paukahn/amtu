import os
from getpass import getpass
from library.security.data_protector import encrypt, decrypt
from library.atomic_io import atomic_write_bytes
from library.helper_functions import confirm

MAIL_CONFIG_PATH = "mail.email"

def configure_email(key, hmac_key):
    print("\n📧 Configurar correo raíz (solo un correo).")

    existing_email = ""
    existing_password = ""

    # Leer configuración si existe
    if os.path.exists(MAIL_CONFIG_PATH):
        try:
            decrypted = decrypt(MAIL_CONFIG_PATH, key, hmac_key)
            lines = decrypted.splitlines()
            data = {}
            for line in lines:
                if "=" in line:
                    k, v = map(str.strip, line.split("=", 1))  # Maneja espacios alrededor del "="
                    data[k] = v
            existing_email = data.get("email", "")
            existing_password = data.get("password", "")
        except Exception:
            pass

    email = input(f"Correo actual [{existing_email}]: ").strip() or existing_email
    password = getpass("Contraseña (se mantiene si vacía): ")
    if not password:
        password = existing_password

    # Guardar configuración
    lines_to_save = [
        f"email = {email}",
        f"password = {password}"
    ]
    full_text = "\n".join(lines_to_save).strip() + "\n"
    encrypted = encrypt(full_text.encode("utf-8"), key, hmac_key)
    atomic_write_bytes(MAIL_CONFIG_PATH, encrypted, backup=True)

    print("✅ Configuración de correo guardada.")

def show_current_email(key, hmac_key):
    if not os.path.exists(MAIL_CONFIG_PATH):
        print("📭 No hay configuración de correo.")
        return

    try:
        decrypted = decrypt(MAIL_CONFIG_PATH, key, hmac_key)
        lines = [line.strip() for line in decrypted.splitlines() if "=" in line]
        data = {}
        for line in lines:
            k, v = map(str.strip, line.split("=", 1))  # Maneja espacios
            data[k] = v
        email = data.get("email", "(no definido)")
        print(f"📧 Correo actual: {email}")
    except Exception:
        print("❌ No se pudo leer el correo actual.")

def show_email_config(key, hmac_key):
    if not confirm("\u26a0\ufe0f Esto mostrará todos los secretos en texto plano. ¿Estás seguro?"):
        print("❌ Operación cancelada.")
        return

    if not os.path.exists(MAIL_CONFIG_PATH):
        print("📭 No hay configuración de correo.")
        return

    try:
        decrypted = decrypt(MAIL_CONFIG_PATH, key, hmac_key)
        print("\n📫 Contenido del archivo de correo:\n")
        print(decrypted)
        print()
    except Exception as e:
        print(f"❌ Error al descifrar el archivo de correo: {e}")