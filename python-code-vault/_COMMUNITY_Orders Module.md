---
type: community
cohesion: 0.16
members: 18
---

# Orders Module

**Cohesion:** 0.16 - loosely connected
**Members:** 18 nodes

## Members
- [[Copia el CSV final transformado al mismo backup (best-effort, tras transformar).]] - rationale - orders.py
- [[Guarda el backup DURABLE de los datos crudos de Amazon y devuelve la ruta.]] - rationale - orders.py
- [[Módulo de pedidos reportes de órdenes (TSV + XML) - SAP - FTP (async).  Pase]] - rationale - orders.py
- [[_clean_tsv_lines()]] - code - orders.py
- [[_process_region()]] - code - orders.py
- [[_process_region_guarded()]] - code - orders.py
- [[_report_types()]] - code - orders.py
- [[_run_report_safe()]] - code - orders.py
- [[_run_xml()]] - code - orders.py
- [[_safe_remove()]] - code - orders.py
- [[_transform_and_deliver()]] - code - orders.py
- [[_write_text()]] - code - orders.py
- [[archive_final()]] - code - orders.py
- [[archive_raw()]] - code - orders.py
- [[extract_xml_info()]] - code - orders.py
- [[orders.py]] - code - orders.py
- [[process_orders_account()]] - code - orders.py
- [[run_report degradando «no completado»«throttled» a None (como antes).]] - rationale - orders.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Orders_Module
SORT file.name ASC
```

## Connections to other communities
- 8 edges to [[_COMMUNITY_Mailer]]
- 8 edges to [[_COMMUNITY_Stock Module]]
- 7 edges to [[_COMMUNITY_SP-API Exceptions]]
- 5 edges to [[_COMMUNITY_Marketplace Catalog]]
- 5 edges to [[_COMMUNITY_Applications Config]]
- 3 edges to [[_COMMUNITY_Acronyms Config]]
- 3 edges to [[_COMMUNITY_Runner & VAT]]
- 2 edges to [[_COMMUNITY_Common Config]]
- 2 edges to [[_COMMUNITY_Async Transport & Retry]]
- 1 edge to [[_COMMUNITY_DataTransformer (SAP)]]
- 1 edge to [[_COMMUNITY_FTP Config]]

## Top bridge nodes
- [[orders.py]] - degree 38, connects to 10 communities
- [[_process_region()]] - degree 12, connects to 6 communities
- [[process_orders_account()]] - degree 6, connects to 4 communities
- [[_run_report_safe()]] - degree 6, connects to 3 communities
- [[_transform_and_deliver()]] - degree 4, connects to 2 communities