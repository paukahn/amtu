import os
from library.security.data_protector import encrypt, decrypt
from library.atomic_io import atomic_write_bytes
from classes.config.Token import TokensConfig
from library.helper_functions import confirm, mask_secret

TOKENS_PATH = "tokens.amztok"

def show_all_tokens(key, hmac_key):
    if not confirm("⚠️ Esto mostrará todos los refresh_tokens en texto plano. ¿Estás seguro?"):
        print("❌ Operación cancelada.")
        return
    if os.path.exists(TOKENS_PATH):
        decrypted = decrypt(TOKENS_PATH, key, hmac_key)
        print("\n📁 Contenido completo descifrado:\n")
        print(decrypted)
    else:
        print("📁 No hay archivo de configuración cifrado.")

def list_tokens(key, hmac_key):
    config = TokensConfig(key=key, hmac_key=hmac_key)
    all_tokens = config.get_all_tokens()

    # Filtrar cuentas que tengan al menos un token no vacío
    non_empty_accounts = {
        acc: {k: v for k, v in regions.items() if v and v.strip()}
        for acc, regions in all_tokens.items()
        if any(v and v.strip() for v in regions.values())
    }

    if non_empty_accounts:
        print("\n📋 Cuentas registradas:")
        for account, regions in non_empty_accounts.items():
            print(f"  - {account}")
            for region, token in regions.items():
                # Enmascarado: el volcado completo vive en show_all_tokens (con confirm).
                print(f"      {region}: {mask_secret(token)}")
    else:
        print("ℹ️ No hay cuentas aún.")

def edit_token_section(lines, account_name, new_kv_lines):
    """
    Inserta o actualiza la sección de 'account_name' en las líneas del archivo.
    Omite cualquier línea de token vacío.
    """
    account_lower = account_name.lower()
    new_lines = []
    section_found = False
    i = 0

    # Filtrar solo las líneas no vacías de tokens
    new_kv_lines = [line for line in new_kv_lines if '=' in line and line.split('=', 1)[1].strip()]

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Detecta secciones
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1].strip().lower()
            if current_section == account_lower:
                # Sección encontrada: reemplazar con new_kv_lines
                section_found = True
                new_lines.append(f"[{account_name}]")
                new_lines.extend(new_kv_lines)
                i += 1
                # Saltar líneas antiguas de esta sección
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith("[") and next_line.endswith("]"):
                        break
                    i += 1
                continue

        new_lines.append(line)
        i += 1

    # Si no existía la sección, agregar al final
    if not section_found and new_kv_lines:
        if new_lines and new_lines[-1].strip() != "":
            new_lines.append("")  # Separador de línea
        new_lines.append(f"[{account_name}]")
        new_lines.extend(new_kv_lines)
        new_lines.append("")

    return new_lines

def add_or_edit_token(key, hmac_key):
    account_name = input("Nombre de la cuenta: ").strip()
    if not account_name:
        print("⚠️ Nombre inválido.")
        return

    config = TokensConfig(key=key, hmac_key=hmac_key)
    existing_tokens = config.get_account_tokens(account_name)

    new_kv_lines = []
    for region in ["na", "eu"]:
        current_val = existing_tokens.get(f"refresh_token_{region}", "")
        # Prompt enmascarado: el token vigente no debe quedar en el scrollback
        # de la terminal; entrada vacía conserva el valor actual.
        token = input(f"Refresh token {region} [{mask_secret(current_val)}]: ").strip() or current_val
        if token and token.strip():  # <-- solo añade si no está vacío
            new_kv_lines.append(f"refresh_token_{region} = {token}")

    if not new_kv_lines:
        print("⚠️ No se proporcionó ningún token válido. Operación cancelada.")
        return

    lines = decrypt(TOKENS_PATH, key, hmac_key).splitlines() if os.path.exists(TOKENS_PATH) else []
    new_lines = edit_token_section(lines, account_name, new_kv_lines)

    encrypted = encrypt(("\n".join(new_lines).rstrip() + "\n").encode("utf-8"), key, hmac_key)
    # Atómico + .bak: una escritura parcial del blob cifrado invalida el HMAC
    # y perdía TODOS los refresh-tokens sin copia.
    atomic_write_bytes(TOKENS_PATH, encrypted, backup=True)

    print(f"\n✅ Tokens de '{account_name}' guardados correctamente.")

def _list_token_account_names(key, hmac_key):
    """Lista SOLO los nombres de cuenta con tokens, sin volcar los secretos.

    delete_token usaba list_tokens(), que imprime cada refresh_token completo en
    claro: simplemente entrar a «Eliminar tokens» filtraba todos los tokens a la
    consola/historial sin confirm. El resto del CLI (delete_app, delete_ftp_config)
    muestra solo nombres; el volcado en claro queda en show_all_tokens, con confirm.
    """
    config = TokensConfig(key=key, hmac_key=hmac_key)
    names = [acc for acc, regions in config.get_all_tokens().items()
             if any(v and v.strip() for v in regions.values())]
    if names:
        print("\n📋 Cuentas con tokens:")
        for n in names:
            print(f"  - {n}")
    else:
        print("ℹ️ No hay cuentas con tokens.")


def delete_token(key, hmac_key):
    _list_token_account_names(key, hmac_key)
    account_name = input("\n❌ Nombre de la cuenta a eliminar: ").strip()
    if not account_name:
        print("⚠️ Nombre inválido.")
        return

    if not os.path.exists(TOKENS_PATH):
        print("📁 No hay archivo de configuración cifrado.")
        return

    decrypted = decrypt(TOKENS_PATH, key, hmac_key)
    lines = decrypted.splitlines()
    new_lines, in_section, deleted = [], False, False
    account_lower = account_name.lower()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1].strip().lower()
            in_section = current_section == account_lower
            if in_section:
                deleted = True
                continue
        if not in_section:
            new_lines.append(line)

    if deleted:
        full_text = "\n".join(new_lines).strip() + "\n"
        encrypted = encrypt(full_text.encode("utf-8"), key, hmac_key)
        atomic_write_bytes(TOKENS_PATH, encrypted, backup=True)
        print(f"✅ Tokens de '{account_name}' eliminados correctamente.")
    else:
        print(f"ℹ️ Cuenta '{account_name}' no encontrada.")
