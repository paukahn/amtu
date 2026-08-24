---
type: community
cohesion: 0.25
members: 11
---

# Mailer

**Cohesion:** 0.25 - loosely connected
**Members:** 11 nodes

## Members
- [[Envía `body` a todos los correos de configemails.txt.      Carga MailConfig UNA]] - rationale - library/mailer.py
- [[Envía un correo usando SMTP seguro.     param recipient Destinatario     para]] - rationale - library/mailer.py
- [[F10 SMTP hostport configurable in mail.email]] - rationale - REFACTORING.md
- [[F24b stock sanity-guard (min valid SKU ratio, mail alert, do not publish)]] - rationale - REFACTORING.md
- [[Imprime mensajes de error o advertencia.      Args         message (str  bytes]] - rationale - library/logging_helpers/message_processor.py
- [[Notificaciones por correo (SMTP). Separado de helper_functions en el pase 2.  El]] - rationale - library/mailer.py
- [[error()]] - code - library/logging_helpers/message_processor.py
- [[load_mails()]] - code - library/file_explorer.py
- [[mailer.py]] - code - library/mailer.py
- [[notify_error_mail()]] - code - library/mailer.py
- [[send_mail()]] - code - library/mailer.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Mailer
SORT file.name ASC
```

## Connections to other communities
- 9 edges to [[_COMMUNITY_File IO]]
- 8 edges to [[_COMMUNITY_Orders Module]]
- 8 edges to [[_COMMUNITY_Stock Module]]
- 4 edges to [[_COMMUNITY_Runner & VAT]]
- 4 edges to [[_COMMUNITY_Marketplace Catalog]]
- 4 edges to [[_COMMUNITY_Master-Key Crypto & CLI]]
- 3 edges to [[_COMMUNITY_Mail Config]]
- 3 edges to [[_COMMUNITY_Logging Helpers]]
- 3 edges to [[_COMMUNITY_LWA Token Provider]]
- 1 edge to [[_COMMUNITY_Config Save]]
- 1 edge to [[_COMMUNITY_FTP Config]]

## Top bridge nodes
- [[error()]] - degree 35, connects to 9 communities
- [[mailer.py]] - degree 14, connects to 5 communities
- [[notify_error_mail()]] - degree 10, connects to 5 communities
- [[send_mail()]] - degree 6, connects to 3 communities
- [[load_mails()]] - degree 4, connects to 1 community