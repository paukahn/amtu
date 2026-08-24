---
type: community
cohesion: 0.24
members: 10
---

# Mail Config

**Cohesion:** 0.24 - loosely connected
**Members:** 10 nodes

## Members
- [[.__init__()_6]] - code - classes/config/Mail.py
- [[.get_email()]] - code - classes/config/Mail.py
- [[.get_password()]] - code - classes/config/Mail.py
- [[.get_smtp_host()]] - code - classes/config/Mail.py
- [[.get_smtp_port()]] - code - classes/config/Mail.py
- [[.load_config()_3]] - code - classes/config/Mail.py
- [[.save_config()]] - code - classes/config/Mail.py
- [[.set_credentials()]] - code - classes/config/Mail.py
- [[Cuenta SMTP raíz (mail.email, cifrado).      Novedad del pase 2 `smtp_host` y `]] - rationale - classes/config/Mail.py
- [[MailConfig]] - code - classes/config/Mail.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Mail_Config
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Config Save]]
- 3 edges to [[_COMMUNITY_Mailer]]
- 2 edges to [[_COMMUNITY_Stock Config]]
- 1 edge to [[_COMMUNITY_Acronyms Config]]
- 1 edge to [[_COMMUNITY_Config Read]]
- 1 edge to [[_COMMUNITY_FTP Config]]

## Top bridge nodes
- [[MailConfig]] - degree 15, connects to 4 communities
- [[.load_config()_3]] - degree 6, connects to 3 communities
- [[.save_config()]] - degree 4, connects to 2 communities