---
type: community
cohesion: 0.28
members: 13
---

# Stock Module

**Cohesion:** 0.28 - loosely connected
**Members:** 13 nodes

## Members
- [[Descarga el stock remoto de una región, construye el feed y lo envía.      `guar]] - rationale - stock.py
- [[Imprime mensajes informativos (success).      Args         message (str  bytes]] - rationale - library/logging_helpers/message_processor.py
- [[Módulo de stockprecios feed JSON_LISTINGS_FEED (async).  Pase 2 - Contrato nu]] - rationale - stock.py
- [[_send_region_feed()]] - code - stock.py
- [[_verify_feed()]] - code - stock.py
- [[archive_sent_stock_tsv()]] - code - library/file_explorer.py
- [[info()]] - code - library/logging_helpers/message_processor.py
- [[main()_1]] - code - orders.py
- [[main()_2]] - code - stock.py
- [[main()_3]] - code - trackings.py
- [[process_account()]] - code - stock.py
- [[run_module_sync()]] - code - library/runner.py
- [[stock.py_1]] - code - stock.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Stock_Module
SORT file.name ASC
```

## Connections to other communities
- 12 edges to [[_COMMUNITY_File IO]]
- 11 edges to [[_COMMUNITY_Marketplace Catalog]]
- 10 edges to [[_COMMUNITY_Runner & VAT]]
- 8 edges to [[_COMMUNITY_Mailer]]
- 8 edges to [[_COMMUNITY_Orders Module]]
- 5 edges to [[_COMMUNITY_SP-API Exceptions]]
- 3 edges to [[_COMMUNITY_Logging Helpers]]
- 2 edges to [[_COMMUNITY_Common Config]]
- 2 edges to [[_COMMUNITY_Stock Config]]
- 2 edges to [[_COMMUNITY_Async Transport & Retry]]
- 2 edges to [[_COMMUNITY_LWA Token Provider]]
- 1 edge to [[_COMMUNITY_FTP Config]]

## Top bridge nodes
- [[stock.py_1]] - degree 29, connects to 9 communities
- [[info()]] - degree 35, connects to 8 communities
- [[process_account()]] - degree 9, connects to 5 communities
- [[run_module_sync()]] - degree 10, connects to 3 communities
- [[_send_region_feed()]] - degree 8, connects to 2 communities