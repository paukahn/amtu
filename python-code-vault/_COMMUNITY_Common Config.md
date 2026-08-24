---
type: community
cohesion: 0.16
members: 14
---

# Common Config

**Cohesion:** 0.16 - loosely connected
**Members:** 14 nodes

## Members
- [[.__init__()_3]] - code - classes/config/Common.py
- [[.create_default_config()]] - code - classes/config/Common.py
- [[.get_mode()]] - code - classes/config/Common.py
- [[.get_orders_folder()]] - code - classes/config/Common.py
- [[.get_reports_folder()]] - code - classes/config/Common.py
- [[.get_stock_folder()]] - code - classes/config/Common.py
- [[.get_stock_guard_min_rows()]] - code - classes/config/Common.py
- [[.get_stock_min_valid_ratio()]] - code - classes/config/Common.py
- [[.get_trackings_folder()]] - code - classes/config/Common.py
- [[.load_config()_1]] - code - classes/config/Common.py
- [[CommonConfig]] - code - classes/config/Common.py
- [[Fracción mínima de filas con SKU válido para publicar el feed (sanity-guard).]] - rationale - classes/config/Common.py
- [[Maneja configuración global común desde common.ini.     reports_folder es obliga]] - rationale - classes/config/Common.py
- [[Nº de filas a partir del cual aplicar el sanity-guard del stock.]] - rationale - classes/config/Common.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Common_Config
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Config Save]]
- 3 edges to [[_COMMUNITY_File IO]]
- 2 edges to [[_COMMUNITY_Stock Config]]
- 2 edges to [[_COMMUNITY_Logging Helpers]]
- 2 edges to [[_COMMUNITY_Runner & VAT]]
- 2 edges to [[_COMMUNITY_Orders Module]]
- 2 edges to [[_COMMUNITY_Stock Module]]
- 1 edge to [[_COMMUNITY_Acronyms Config]]
- 1 edge to [[_COMMUNITY_Marketplace Catalog]]

## Top bridge nodes
- [[CommonConfig]] - degree 26, connects to 9 communities
- [[.load_config()_1]] - degree 6, connects to 2 communities