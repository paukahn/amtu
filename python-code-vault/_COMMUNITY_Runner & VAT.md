---
type: community
cohesion: 0.15
members: 17
---

# Runner & VAT

**Cohesion:** 0.15 - loosely connected
**Members:** 17 nodes

## Members
- [[(start, end) ISO-8601 del mes natural anterior, como usaba el original.]] - rationale - vat_report.py
- [[DataFrame_1]] - code
- [[F12 invalid config raises ConfigError instead of sys.exit(1)]] - rationale - REFACTORING.md
- [[F15 debug mode restored (runner derives debug - AccountClients - AsyncTransport)]] - rationale - REFACTORING.md
- [[F16 account isolation restored (except Exception + return_exceptions)]] - rationale - REFACTORING.md
- [[F8 account regions (EUNA) processed in parallel in orders]] - rationale - REFACTORING.md
- [[Módulo VAT reporte GET_VAT_TRANSACTION_DATA (async).  Pase 2 - Contrato nuevo]] - rationale - vat_report.py
- [[RunContext]] - code - library/runner.py
- [[Runner compartido para los módulos (orders  stock  trackings  vat).  Orquesta]] - rationale - library/runner.py
- [[_prev_month_window()]] - code - vat_report.py
- [[_tsv_text_to_dataframe()]] - code - vat_report.py
- [[main()_4]] - code - vat_report.py
- [[process_vat_account()]] - code - vat_report.py
- [[run_module()]] - code - library/runner.py
- [[runner.py]] - code - library/runner.py
- [[set_log_context()]] - code - library/logging_helpers/message_processor.py
- [[vat_report.py]] - code - vat_report.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Runner__VAT
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_Stock Module]]
- 4 edges to [[_COMMUNITY_File IO]]
- 4 edges to [[_COMMUNITY_Marketplace Catalog]]
- 4 edges to [[_COMMUNITY_Mailer]]
- 3 edges to [[_COMMUNITY_Polling Config]]
- 3 edges to [[_COMMUNITY_Async Transport & Retry]]
- 3 edges to [[_COMMUNITY_Client Factory]]
- 3 edges to [[_COMMUNITY_Orders Module]]
- 2 edges to [[_COMMUNITY_Accounts Config]]
- 2 edges to [[_COMMUNITY_Common Config]]
- 2 edges to [[_COMMUNITY_Stock Config]]
- 2 edges to [[_COMMUNITY_Logging Helpers]]
- 2 edges to [[_COMMUNITY_Master-Key Crypto & CLI]]
- 1 edge to [[_COMMUNITY_Applications Config]]
- 1 edge to [[_COMMUNITY_SP-API Exceptions]]
- 1 edge to [[_COMMUNITY_LWA Token Provider]]
- 1 edge to [[_COMMUNITY_Runner Isolation Test]]

## Top bridge nodes
- [[runner.py]] - degree 23, connects to 12 communities
- [[vat_report.py]] - degree 17, connects to 6 communities
- [[run_module()]] - degree 9, connects to 6 communities
- [[set_log_context()]] - degree 12, connects to 5 communities
- [[process_vat_account()]] - degree 6, connects to 3 communities