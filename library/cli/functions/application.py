import os
from library.security.data_protector import encrypt, decrypt
from library.atomic_io import atomic_write_bytes
from classes.config.Applications import ApplicationsConfig
from library.helper_functions import confirm, mask_secret

CONFIG_PATH = "applications.amzapps"

def show_all(key, hmac_key):
    if not confirm("⚠️ Esto mostrará todos los secretos en texto plano. ¿Estás seguro?"):
        print("❌ Operación cancelada.")
        return
    if os.path.exists(CONFIG_PATH):
        decrypted = decrypt(CONFIG_PATH, key, hmac_key)
        print("\n📁 Contenido completo descifrado:\n")
        print(decrypted)
    else:
        print("📁 No hay archivo de configuración cifrado.")

def list_apps(key, hmac_key, show_disabled=False):
    if os.path.exists(CONFIG_PATH):
        config = ApplicationsConfig(directory="", key=key, hmac_key=hmac_key, original=True)
        apps = config.get_applications_original() if show_disabled else config.get_active_applications_original()
        if apps:
            print("\n📋 Aplicaciones registradas:")
            for name, data in apps.items():
                status = " (desactivada)" if not data.get("enabled", True) else ""
                print(f"  - {name}{status}")
        else:
            print("ℹ️ No hay aplicaciones aún.")
    else:
        print("📁 No hay archivo de configuración cifrado.")

def delete_app(key, hmac_key):
    list_apps(key, hmac_key, show_disabled=True)
    app_name = input("\n❌ Nombre de la aplicación a eliminar: ").strip()
    if not app_name or not os.path.exists(CONFIG_PATH):
        print("⚠️ Nombre inválido o no hay archivo de configuración.")
        return
    decrypted = decrypt(CONFIG_PATH, key, hmac_key)
    lines = decrypted.splitlines()
    new_lines, in_section, deleted = [], False, False
    section_to_delete = app_name.lower()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1].strip().lower()
            in_section = current_section == section_to_delete
            if in_section:
                deleted = True
                continue
        if not in_section:
            new_lines.append(line)
    if deleted:
        full_text = "\n".join(new_lines).strip() + "\n"
        encrypted = encrypt(full_text.encode("utf-8"), key, hmac_key)
        atomic_write_bytes(CONFIG_PATH, encrypted, backup=True)
        print(f"✅ Aplicación '{app_name}' eliminada correctamente.")
    else:
        print(f"ℹ️ Aplicación '{app_name}' no encontrada.")

def toggle_app(key, hmac_key, enable=True):
    config = ApplicationsConfig(directory="", key=key, hmac_key=hmac_key, original=True)
    list_apps(key, hmac_key, show_disabled=True)
    action = "activar" if enable else "desactivar"
    app_name = input(f"\n{ '✅' if enable else '🚫' } Nombre de la aplicación a {action}: ").strip()
    if not app_name:
        print("⚠️ Nombre no válido.")
        return
    if config.set_enabled(app_name, enable):
        config.save()
        print(f"{ '✅' if enable else '🛑' } Aplicación '{app_name}' {'activada' if enable else 'desactivada'}.")
    else:
        print(f"ℹ️ Aplicación '{app_name}' no encontrada.")

def edit_app_section(lines, app_name, new_kv_lines):
    app_lower = app_name.lower()
    new_lines = []
    in_section = section_found = False
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1].strip().lower()
            if current_section == app_lower:
                section_found = True
                in_section = True
                new_lines.append(f"[{app_name}]")
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
        new_lines.append(f"[{app_name}]")
        new_lines.extend(new_kv_lines)
        new_lines.append("")
    if new_lines and new_lines[-1].strip() != "":
        new_lines.append("")
    return new_lines

def create_or_edit_application(key, hmac_key):
    app_name = input("\n🔧 Nombre de la aplicación: ").strip()
    if not app_name:
        print("⚠️ Nombre inválido.")
        return
    apps = {}
    if os.path.exists(CONFIG_PATH):
        config = ApplicationsConfig(directory="", key=key, hmac_key=hmac_key, original=True)
        apps = config.get_applications_original()
    existing = apps.get(app_name, {})
    client_id = input(f"🆔 client_id [{existing.get('client_id','')}]: ").strip() or existing.get('client_id','')
    if not client_id:
        print("⚠️ Identificador del cliente inválido.")
        return
    # Prompt enmascarado: el client_secret vigente no debe quedar en el
    # scrollback; entrada vacía conserva el valor actual.
    client_secret = input(f"🔑 client_secret [{mask_secret(existing.get('client_secret',''))}]: ").strip() or existing.get('client_secret','')
    if not client_secret:
        print("⚠️ Secreto del cliente inválido.")
        return
    enabled_input = input(f"¿Activar aplicación? [S/n] (actual: {'Sí' if existing.get('enabled',True) else 'No'}): ").strip().lower()
    enabled = existing.get('enabled', True) if enabled_input=="" else enabled_input in ["s","si","yes","y"]
    lines = decrypt(CONFIG_PATH, key, hmac_key).splitlines() if os.path.exists(CONFIG_PATH) else []
    kv_lines = [f"client_id = {client_id}", f"client_secret = {client_secret}", f"enabled = {'true' if enabled else 'false'}"]
    new_lines = edit_app_section(lines, app_name, kv_lines)
    encrypted = encrypt(("\n".join(new_lines).rstrip() + "\n").encode("utf-8"), key, hmac_key)
    atomic_write_bytes(CONFIG_PATH, encrypted, backup=True)
    print(f"\n✅ Aplicación '{app_name}' guardada con éxito.")