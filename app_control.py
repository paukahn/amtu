import sys, os
from getpass import getpass
from Crypto.Random import get_random_bytes
from classes.config import ConfigError
from library.security import encrypt_keys, load_keys
from library.cli.menus import show_all, list_apps, delete_app, tokens_menu_loop, interactive_edit_loop

SECRET_ENV = ".env.secret"
SECRET_BIN = "secret_keys.bin"

def main():
    # Anclar el cwd: todas las rutas (config/, tokens.amztok, .env.secret…)
    # son relativas a la raíz del proyecto.
    from library.paths import ensure_project_cwd
    ensure_project_cwd()
    # Inicialización de llaves
    if not os.path.exists(SECRET_ENV) and not os.path.exists(SECRET_BIN):
        print("🔐 Primera vez: crea una contraseña maestra.")
        password = getpass("Contraseña maestra: ")
        key = get_random_bytes(32)
        hmac_key = get_random_bytes(32)
        encrypt_keys(key, hmac_key, password)
        # Guardar también en .env.secret para ejecución automática (cron).
        # Formato: 64 bytes crudos (key[32] + hmac_key[32]), tal como los
        # espera key_manager.load_keys(auto=True). NO usar texto hex.
        # Se crea con 0600 desde el primer byte (en Linux; en Windows los ACL
        # NTFS no usan estos bits). O_EXCL: nunca pisar un fichero existente.
        fd = os.open(SECRET_ENV, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(key + hmac_key)
        print("✅ Claves generadas y guardadas.")
        print("   ℹ️ En el servidor: mueve el fichero fuera del proyecto y apúntalo con")
        print("      AMTUBB_KEYS_FILE=/ruta/segura/amtubb.keys (o usa AMTUBB_MASTER_KEYS=base64).")
    # Cargar llaves
    try:
        auto = os.environ.get("AUTO_LOAD_KEYS","0")=="1"
        key, hmac_key = load_keys(auto=auto)
    except Exception as e:
        print(f"❌ No se pudieron cargar las llaves: {e}")
        sys.exit(1)
    # Comandos CLI. Las clases de config ya no hacen sys.exit: capturamos
    # ConfigError aquí para mostrar un mensaje limpio en vez de un traceback.
    try:
        if len(sys.argv)>1:
            cmd = sys.argv[1].lower()
            if cmd=="--show-all": show_all(key,hmac_key)
            elif cmd=="--list": list_apps(key,hmac_key,False)
            elif cmd=="--list-all": list_apps(key,hmac_key,True)
            elif cmd=="--delete": delete_app(key,hmac_key)
            # El original llamaba tokens_menu_loop() SIN llaves: TypeError seguro.
            elif cmd=="--tokens": tokens_menu_loop(key,hmac_key)
            else: print(f"❌ Comando desconocido: {cmd}")
        else:
            interactive_edit_loop(key,hmac_key)
    except ConfigError as e:
        print(f"❌ Error de configuración: {e}")
        sys.exit(1)

if __name__=="__main__":
    main()
