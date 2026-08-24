---
type: community
cohesion: 0.26
members: 12
---

# Stock Config

**Cohesion:** 0.26 - loosely connected
**Members:** 12 nodes

## Members
- [[.__init__()_8]] - code - classes/config/Stock.py
- [[.get_all_stocks()]] - code - classes/config/Stock.py
- [[.get_seller_id()]] - code - classes/config/Stock.py
- [[.get_stock_url()]] - code - classes/config/Stock.py
- [[.get_store_stock()]] - code - classes/config/Stock.py
- [[.load_stocks()]] - code - classes/config/Stock.py
- [[.stocks_list()]] - code - classes/config/Stock.py
- [[Carga la configuración de stocks desde stock.ini.     Claves permitidas las que]] - rationale - classes/config/Stock.py
- [[ConfigError]] - code - classes/config/base.py
- [[Configuración ausente, ilegible o inválida.]] - rationale - classes/config/base.py
- [[Stock.py]] - code - classes/config/Stock.py
- [[StockConfig]] - code - classes/config/Stock.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Stock_Config
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_Config Save]]
- 5 edges to [[_COMMUNITY_Config Read]]
- 3 edges to [[_COMMUNITY_Accounts Config]]
- 3 edges to [[_COMMUNITY_Polling Config]]
- 3 edges to [[_COMMUNITY_Acronyms Config]]
- 3 edges to [[_COMMUNITY_Config Parser (base)]]
- 2 edges to [[_COMMUNITY_Common Config]]
- 2 edges to [[_COMMUNITY_Mail Config]]
- 2 edges to [[_COMMUNITY_Stock Module]]
- 2 edges to [[_COMMUNITY_Runner & VAT]]
- 1 edge to [[_COMMUNITY_Master-Key Crypto & CLI]]
- 1 edge to [[_COMMUNITY_Applications Config]]
- 1 edge to [[_COMMUNITY_SP-API Exceptions]]
- 1 edge to [[_COMMUNITY_save_sections Tests]]

## Top bridge nodes
- [[ConfigError]] - degree 32, connects to 13 communities
- [[Stock.py]] - degree 7, connects to 4 communities
- [[.load_stocks()]] - degree 5, connects to 3 communities
- [[StockConfig]] - degree 13, connects to 2 communities