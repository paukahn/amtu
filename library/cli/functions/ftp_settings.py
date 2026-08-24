import os
from library.security.data_protector import encrypt, decrypt
from library.atomic_io import atomic_write_bytes
from classes.config import FTPConfig
from library.helper_functions import confirm

CONFIG_PATH = "ftp_accounts.amzaccs"


def list_active_ftp_configs(key, hmac_key):
    if os.path.exists(CONFIG_PATH):
        config = FTPConfig(directory="", key=key, hmac_key=hmac_key)
        accounts = config.accounts

        active_apps = {k: v for k, v in accounts.items()
                       if str(v.get('is_active', 'false')).lower() in ['true', '1', 'yes']}

        if active_apps:
            print("\n🟢 Cuentas de transporte ACTIVAS:")
            for name, data in active_apps.items():
                mode = data.get('ftp_mode', 'ftp').upper()
                print(f"  - {name} [{mode}] -> {data.get('host')}")
        else:
            print("\nℹ️ No hay cuentas de transporte activas en este momento.")
    else:
        print("📁 No hay archivo de configuración cifrado.")

def show_all_transport(key, hmac_key):
    if not confirm("⚠️ Esto mostrará todas las credenciales FTP/SFTP en texto plano. ¿Estás seguro?"):
        print("❌ Operación cancelada.")
        return
    if os.path.exists(CONFIG_PATH):
        decrypted = decrypt(CONFIG_PATH, key, hmac_key)
        print("\n📁 Configuración de transporte descifrada:\n")
        print(decrypted)
    else:
        print("📁 No hay archivo de configuración de transporte.")


def list_ftp_configs(key, hmac_key, show_disabled=True):
    if os.path.exists(CONFIG_PATH):
        config = FTPConfig(directory="", key=key, hmac_key=hmac_key)
        accounts = config.accounts

        if accounts:
            print("\n📋 Cuentas de transporte registradas:")
            for name, data in accounts.items():
                # Проверка ключа is_active
                active_val = str(data.get('is_active', 'false')).lower()
                active = active_val in ['true', '1', 'yes']

                if not show_disabled and not active:
                    continue
                status = "" if active else " (desactivada)"
                mode = data.get('ftp_mode', 'ftp').upper()
                print(f"  - {name} [{mode}]{status}")
        else:
            print("ℹ️ No hay cuentas de transporte aún.")
    else:
        print("📁 No hay archivo de configuración cifrado.")


def delete_ftp_config(key, hmac_key):
    list_ftp_configs(key, hmac_key, show_disabled=True)
    acc_name = input("\n❌ Nombre de la cuenta de transporte a eliminar: ").strip().lower()
    if not acc_name or not os.path.exists(CONFIG_PATH):
        print("⚠️ Nombre inválido o no hay archivo.")
        return

    decrypted = decrypt(CONFIG_PATH, key, hmac_key)
    lines = decrypted.splitlines()
    new_lines, in_section, deleted = [], False, False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1].strip().lower()
            in_section = (current_section == acc_name)
            if in_section:
                deleted = True
                continue
        if not in_section:
            new_lines.append(line)

    if deleted:
        full_text = "\n".join(new_lines).strip() + "\n"
        encrypted = encrypt(full_text.encode("utf-8"), key, hmac_key)
        atomic_write_bytes(CONFIG_PATH, encrypted, backup=True)
        print(f"✅ Cuenta '{acc_name}' eliminada correctamente.")
    else:
        print(f"ℹ️ Cuenta '{acc_name}' no encontrada.")


def toggle_ftp_active(key, hmac_key, enable=True):
    config = FTPConfig(directory="", key=key, hmac_key=hmac_key)
    list_ftp_configs(key, hmac_key, show_disabled=True)
    action = "activar" if enable else "desactivar"
    acc_name = input(f"\n{'✅' if enable else '🚫'} Nombre de la cuenta a {action}: ").strip().lower()

    if acc_name in config.accounts:
        config.accounts[acc_name]['is_active'] = 'true' if enable else 'false'
        config.save()
        print(f"{'✅' if enable else '🛑'} Transporte '{acc_name}' {'activado' if enable else 'desactivada'}.")
    else:
        print(f"ℹ️ Cuenta '{acc_name}' no encontrada.")


def edit_ftp_section(lines, acc_name, new_kv_lines):
    acc_lower = acc_name.lower()
    new_lines = []
    in_section = section_found = False
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1].strip().lower()
            if current_section == acc_lower:
                section_found = True
                in_section = True
                new_lines.append(f"[{acc_name}]")
                new_lines.extend(new_kv_lines)
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith("[") and next_line.endswith("]"):
                        in_section = False
                        break
                    i += 1
                continue
            else:
                in_section = False
        if not in_section:
            new_lines.append(line)
        i += 1
    if not section_found:
        if new_lines and new_lines[-1].strip() != "":
            new_lines.append("")
        new_lines.append(f"[{acc_name}]")
        new_lines.extend(new_kv_lines)
        new_lines.append("")
    return new_lines


def create_or_edit_ftp_config(key, hmac_key):
    acc_name = input("\n🚀 Nombre de la cuenta de transporte (ej. lladro): ").strip().lower()
    if not acc_name:
        print("⚠️ Nombre inválido.")
        return

    config = FTPConfig(directory="", key=key, hmac_key=hmac_key)
    existing = config.get_account_params(acc_name)

    ftp_mode = input(f"📡 Modo (ftp/sftp) [{existing.get('ftp_mode', 'sftp')}]: ").strip().lower() or existing.get(
        'ftp_mode', 'sftp')
    host = input(f"🌐 Host [{existing.get('host', '')}]: ").strip() or existing.get('host', '')
    user = input(f"👤 Username [{existing.get('username', '')}]: ").strip() or existing.get('username', '')
    password = input(f"🔑 Password [{'***' if existing.get('password') else ''}]: ").strip() or existing.get('password',
                                                                                                            '')
    folder = input(f"📂 Folder IN [{existing.get('folder_in', '/')}]: ").strip() or existing.get('folder_in', '/')
    default_port = '22' if ftp_mode == 'sftp' else '21'
    current_port = existing.get('port') if existing.get('port') else default_port
    port = input(f"🔌 Port [{current_port}]: ").strip() or current_port

    host_key = existing.get('host_key') or ''
    if ftp_mode == 'sftp':
        # Huella SHA256 del host (ssh-keygen -lf /etc/ssh/ssh_host_*.pub).
        # Sin ella el envío funciona pero el servidor NO se verifica (MITM).
        host_key = input(f"🔒 Host key SHA256 [{host_key or 'sin verificar'}]: ").strip() or host_key

    cur_active = str(existing.get('is_active', 'true')).lower() in ['true', '1']
    active_input = input(f"¿Activar transporte? [S/n] (actual: {'Sí' if cur_active else 'No'}): ").strip().lower()
    is_active = 'true' if (active_input == "" or active_input in ["s", "si", "yes", "y"]) else 'false'

    lines = decrypt(CONFIG_PATH, key, hmac_key).splitlines() if os.path.exists(CONFIG_PATH) else []
    kv_lines = [
        f"is_active = {is_active}",
        f"ftp_mode = {ftp_mode}",
        f"host = {host}",
        f"username = {user}",
        f"password = {password}",
        f"folder_in = {folder}",
        f"port = {port}"
    ]
    if host_key:
        kv_lines.append(f"host_key = {host_key}")

    new_lines = edit_ftp_section(lines, acc_name, kv_lines)
    full_text = "\n".join(new_lines).rstrip() + "\n"
    encrypted = encrypt(full_text.encode("utf-8"), key, hmac_key)

    atomic_write_bytes(CONFIG_PATH, encrypted, backup=True)

    print(f"\n✅ Configuración de transporte '{acc_name}' guardada con éxito.")