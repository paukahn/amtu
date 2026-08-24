---
type: community
cohesion: 0.33
members: 7
---

# Config Read

**Cohesion:** 0.33 - loosely connected
**Members:** 7 nodes

## Members
- [[.load_config()]] - code - classes/config/Applications.py
- [[.load_config()_2]] - code - classes/config/FTPTransport.py
- [[.test_missing_file_raises_config_error()]] - code - tests/test_config_base.py
- [[.test_reads_plain_text()]] - code - tests/test_config_base.py
- [[Lee el fichero como texto; si hay llaves, lo descifra antes.]] - rationale - classes/config/base.py
- [[TestReadConfigText]] - code - tests/test_config_base.py
- [[read_config_text()]] - code - classes/config/base.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Config_Read
SORT file.name ASC
```

## Connections to other communities
- 8 edges to [[_COMMUNITY_Config Save]]
- 5 edges to [[_COMMUNITY_Stock Config]]
- 3 edges to [[_COMMUNITY_FTP Config]]
- 2 edges to [[_COMMUNITY_Accounts Config]]
- 2 edges to [[_COMMUNITY_Applications Config]]
- 2 edges to [[_COMMUNITY_Config Parser (base)]]
- 2 edges to [[_COMMUNITY_Polling Config]]
- 1 edge to [[_COMMUNITY_Mail Config]]

## Top bridge nodes
- [[read_config_text()]] - degree 19, connects to 6 communities
- [[.load_config()]] - degree 6, connects to 4 communities
- [[.load_config()_2]] - degree 5, connects to 3 communities
- [[TestReadConfigText]] - degree 4, connects to 2 communities