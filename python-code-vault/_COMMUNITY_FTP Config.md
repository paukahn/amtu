---
type: community
cohesion: 0.12
members: 44
---

# FTP Config

**Cohesion:** 0.12 - loosely connected
**Members:** 44 nodes

## Members
- [[.__init__()_5]] - code - classes/config/FTPTransport.py
- [[.get_account_params()]] - code - classes/config/FTPTransport.py
- [[.has_transport()]] - code - classes/config/FTPTransport.py
- [[.is_active()]] - code - classes/config/FTPTransport.py
- [[.send_file()]] - code - classes/config/FTPTransport.py
- [[Cuentas de transporte FTPSFTP (ftp_accounts.amzaccs, cifrado).      Pase 2 la]] - rationale - classes/config/FTPTransport.py
- [[FTPConfig]] - code - classes/config/FTPTransport.py
- [[Utilidades pequeñas y genéricas (gzip + confirmación CLI).  Adelgazado en el pas]] - rationale - library/helper_functions.py
- [[__init__.py_5]] - code - library/cli/functions/__init__.py
- [[__init__.py_6]] - code - library/cli/menus/__init__.py
- [[application.py]] - code - library/cli/functions/application.py
- [[application_settings_menu()]] - code - library/cli/menus/menus.py
- [[configure_email()]] - code - library/cli/functions/mail_settings.py
- [[confirm()]] - code - library/helper_functions.py
- [[create_or_edit_application()]] - code - library/cli/functions/application.py
- [[create_or_edit_ftp_config()]] - code - library/cli/functions/ftp_settings.py
- [[data_protector.py]] - code - library/security/data_protector.py
- [[decrypt()]] - code - library/security/data_protector.py
- [[delete_app()]] - code - library/cli/functions/application.py
- [[delete_ftp_config()]] - code - library/cli/functions/ftp_settings.py
- [[edit_app_section()]] - code - library/cli/functions/application.py
- [[edit_ftp_section()]] - code - library/cli/functions/ftp_settings.py
- [[encrypt()]] - code - library/security/data_protector.py
- [[ftp_settings.py]] - code - library/cli/functions/ftp_settings.py
- [[helper_functions.py]] - code - library/helper_functions.py
- [[interactive_edit_loop()]] - code - library/cli/menus/menus.py
- [[list_active_ftp_configs()]] - code - library/cli/functions/ftp_settings.py
- [[list_apps()]] - code - library/cli/functions/application.py
- [[list_ftp_configs()]] - code - library/cli/functions/ftp_settings.py
- [[mail_settings.py]] - code - library/cli/functions/mail_settings.py
- [[mail_settings_menu()]] - code - library/cli/menus/menus.py
- [[main()]] - code - app_control.py
- [[menus.py]] - code - library/cli/menus/menus.py
- [[pad()_1]] - code - library/security/data_protector.py
- [[show_all()]] - code - library/cli/functions/application.py
- [[show_all_transport()]] - code - library/cli/functions/ftp_settings.py
- [[show_current_email()]] - code - library/cli/functions/mail_settings.py
- [[show_email_config()]] - code - library/cli/functions/mail_settings.py
- [[toggle_app()]] - code - library/cli/functions/application.py
- [[toggle_ftp_active()]] - code - library/cli/functions/ftp_settings.py
- [[tokens_menu_loop()]] - code - library/cli/menus/menus.py
- [[transport_settings_menu()]] - code - library/cli/menus/menus.py
- [[unpad()_1]] - code - library/security/data_protector.py
- [[¿Hay transporte configurado Y activo para la cuenta]] - rationale - classes/config/FTPTransport.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/FTP_Config
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_Config Save]]
- 6 edges to [[_COMMUNITY_Master-Key Crypto & CLI]]
- 4 edges to [[_COMMUNITY_Applications Config]]
- 4 edges to [[_COMMUNITY_LWA Token Provider]]
- 3 edges to [[_COMMUNITY_Config Read]]
- 2 edges to [[_COMMUNITY_File IO]]
- 1 edge to [[_COMMUNITY_Acronyms Config]]
- 1 edge to [[_COMMUNITY_Orders Module]]
- 1 edge to [[_COMMUNITY_Mailer]]
- 1 edge to [[_COMMUNITY_Mail Config]]
- 1 edge to [[_COMMUNITY_Stock Module]]

## Top bridge nodes
- [[decrypt()]] - degree 19, connects to 4 communities
- [[encrypt()]] - degree 17, connects to 4 communities
- [[FTPConfig]] - degree 16, connects to 4 communities
- [[application.py]] - degree 14, connects to 2 communities
- [[helper_functions.py]] - degree 8, connects to 2 communities