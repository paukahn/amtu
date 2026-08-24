---
type: community
cohesion: 0.20
members: 18
---

# Config Save

**Cohesion:** 0.20 - loosely connected
**Members:** 18 nodes

## Members
- [[.save()]] - code - classes/config/Applications.py
- [[.save()_1]] - code - classes/config/FTPTransport.py
- [[.test_pairs_and_comments()]] - code - tests/test_config_base.py
- [[Applications.py]] - code - classes/config/Applications.py
- [[Base compartida del paquete de configuración (pase 2 del refactor).  Sustituye l]] - rationale - classes/config/base.py
- [[Common.py]] - code - classes/config/Common.py
- [[FTPTransport.py]] - code - classes/config/FTPTransport.py
- [[Mail.py]] - code - classes/config/Mail.py
- [[Parsea `clave = valor` por línea, sin secciones. ''';' a línea completa.]] - rationale - classes/config/base.py
- [[Serializa y guarda el archivo cifrado con el estado actual de las apps.]] - rationale - classes/config/Applications.py
- [[Serializa {sección {clave valor}} al formato `sección`  `k = v`.      Manti]] - rationale - classes/config/base.py
- [[TestParseFlat]] - code - tests/test_config_base.py
- [[Tests del parser base de configuración (classesconfigbase.py).]] - rationale - tests/test_config_base.py
- [[base.py]] - code - classes/config/base.py
- [[config_path()]] - code - classes/config/base.py
- [[parse_flat()]] - code - classes/config/base.py
- [[save_sections()]] - code - classes/config/base.py
- [[test_config_base.py]] - code - tests/test_config_base.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Config_Save
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_Acronyms Config]]
- 10 edges to [[_COMMUNITY_Stock Config]]
- 8 edges to [[_COMMUNITY_Config Read]]
- 7 edges to [[_COMMUNITY_FTP Config]]
- 5 edges to [[_COMMUNITY_Config Parser (base)]]
- 4 edges to [[_COMMUNITY_Mail Config]]
- 3 edges to [[_COMMUNITY_Accounts Config]]
- 3 edges to [[_COMMUNITY_Common Config]]
- 3 edges to [[_COMMUNITY_Polling Config]]
- 3 edges to [[_COMMUNITY_save_sections Tests]]
- 2 edges to [[_COMMUNITY_Applications Config]]
- 1 edge to [[_COMMUNITY_FTPSFTP Transport]]
- 1 edge to [[_COMMUNITY_Mailer]]

## Top bridge nodes
- [[config_path()]] - degree 20, connects to 7 communities
- [[base.py]] - degree 19, connects to 7 communities
- [[Applications.py]] - degree 9, connects to 6 communities
- [[FTPTransport.py]] - degree 9, connects to 6 communities
- [[Mail.py]] - degree 8, connects to 5 communities