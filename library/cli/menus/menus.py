from library.cli.functions import *

def application_settings_menu(key, hmac_key):
    while True:
        print("""
🔧 Ajustes de aplicaciones:
1. Crear o editar aplicación
2. Ver aplicaciones activas
3. Ver todas las aplicaciones
4. Activar aplicación
5. Desactivar aplicación
6. Eliminar aplicación
7. Volver
""")
        choice = input("Seleccione una opción: ").strip()
        if choice=="1": create_or_edit_application(key,hmac_key)
        elif choice=="2": list_apps(key,hmac_key,False)
        elif choice=="3": list_apps(key,hmac_key,True)
        elif choice=="4": toggle_app(key,hmac_key,True)
        elif choice=="5": toggle_app(key,hmac_key,False)
        elif choice=="6": delete_app(key,hmac_key)
        elif choice=="7": break
        else: print("⚠️ Opción inválida.")

def mail_settings_menu(key, hmac_key):
    while True:
        print("""
📫 Ajustes del correo:
1. Configurar correo
2. Ver correo actual
3. Volver
""")
        choice = input("Seleccione una opción: ").strip()
        if choice=="1": configure_email(key,hmac_key)
        elif choice=="2": show_current_email(key,hmac_key)
        elif choice=="3": break
        else: print("⚠️ Opción inválida.")

def tokens_menu_loop(key, hmac_key):
    while True:
        print("""
🔑 Gestión de tokens:
1. Mostrar todos los tokens
2. Añadir/editar tokens
3. Eliminar tokens
4. Volver
""")
        choice = input("Seleccione una opción: ").strip()
        if choice == "1": show_all_tokens(key, hmac_key)
        elif choice == "2": add_or_edit_token(key, hmac_key)
        elif choice == "3": delete_token(key, hmac_key)
        elif choice == "4": break
        else: print("⚠️ Opción inválida.")

def transport_settings_menu(key, hmac_key):
    while True:
        print("""
🚀 Ajustes de transporte (FTP/SFTP):
1. Configurar o editar cuenta FTP/SFTP
2. Ver todas las configuraciones de transporte (resumen)
3. Activar transporte para cuenta
4. Desactivar transporte para cuenta
5. Eliminar configuración de transporte
6. Ver todo el archivo de configuraciones (sensible)
7. Ver cuentas activas
8. Volver
""")
        choice = input("Seleccione una opción: ").strip()
        if choice=="1": create_or_edit_ftp_config(key, hmac_key)
        elif choice=="2": list_ftp_configs(key, hmac_key)
        elif choice=="3": toggle_ftp_active(key, hmac_key, True)
        elif choice=="4": toggle_ftp_active(key, hmac_key, False)
        elif choice=="5": delete_ftp_config(key, hmac_key)
        elif choice == "6": show_all_transport(key, hmac_key)
        elif choice == "7": list_active_ftp_configs(key, hmac_key)
        elif choice=="8": break
        else: print("⚠️ Opción inválida.")

def interactive_edit_loop(key, hmac_key):
    while True:
        print("""
🎛 Menú principal:
1. Ajustes de aplicaciones
2. Ajustes del correo raíz
3. Mostrar contenido de aplicaciones
4. Mostrar contenido del correo
5. Gestión de tokens
6. Ajustes de transporte (FTP/SFTP)
7. Salir
""")
        choice = input("Seleccione una opción: ").strip()
        if choice=="1": application_settings_menu(key, hmac_key)
        elif choice=="2": mail_settings_menu(key, hmac_key)
        elif choice=="3": show_all(key,hmac_key)
        elif choice=="4": show_email_config(key,hmac_key)
        elif choice=="5": tokens_menu_loop(key, hmac_key)
        elif choice=="6": transport_settings_menu(key, hmac_key)
        elif choice=="7":
            print("👋 Saliendo...")
            break
        else: print("⚠️ Opción inválida.")