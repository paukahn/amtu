---
type: community
cohesion: 0.08
members: 60
---

# SP-API Exceptions

**Cohesion:** 0.08 - loosely connected
**Members:** 60 nodes

## Members
- [[.__init__()_12]] - code - library/exceptions.py
- [[.__init__()_19]] - code - tests/test_orders_fallback.py
- [[._call()]] - code - library/spapi_client.py
- [[._poll()]] - code - library/spapi_client.py
- [[.create_feed_document()]] - code - library/spapi_client.py
- [[.create_report()]] - code - library/spapi_client.py
- [[.download_bytes()]] - code - library/spapi_client.py
- [[.download_report_content()]] - code - library/spapi_client.py
- [[.get_feed_result_document()]] - code - library/spapi_client.py
- [[.get_feed_status()]] - code - library/spapi_client.py
- [[.get_report_document()]] - code - library/spapi_client.py
- [[.get_report_status()]] - code - library/spapi_client.py
- [[.get_restricted_data_token()]] - code - library/spapi_client.py
- [[.run_report()]] - code - library/spapi_client.py
- [[.run_report()_1]] - code - tests/test_orders_fallback.py
- [[.s3_put()]] - code - library/spapi_client.py
- [[.send_feed()]] - code - library/spapi_client.py
- [[.send_tracking_feed()]] - code - library/spapi_client.py
- [[.test_400_falls_back_to_general_type()]] - code - tests/test_orders_fallback.py
- [[.test_na_uses_shipping_type()]] - code - tests/test_orders_fallback.py
- [[.test_other_errors_propagate_without_fallback()]] - code - tests/test_orders_fallback.py
- [[.test_poll_exhaustion_degrades_to_none_not_fallback()]] - code - tests/test_orders_fallback.py
- [[.test_success_does_not_fall_back()]] - code - tests/test_orders_fallback.py
- [[AmazonAPIError]] - code - library/exceptions.py
- [[AmazonClient]] - code - library/spapi_client.py
- [[AmazonClient.run_report() report orchestrator]] - code - REFACTORING.md
- [[AmazonError]] - code - library/models.py
- [[AmazonFeedNotReadyError]] - code - library/exceptions.py
- [[AmazonReportNotReadyError]] - code - library/exceptions.py
- [[B2 factorjitter parsed but unused]] - rationale - MIGRATION.md
- [[BaseModel]] - code
- [[Cadena completa create - poll hasta estado terminal - download.          - DO]] - rationale - library/spapi_client.py
- [[CreateFeedDocumentResponse]] - code - library/models.py
- [[CreateFeedResponse]] - code - library/models.py
- [[CreateReportResponse]] - code - library/models.py
- [[Errores generales de la API.      `status_code``body` permiten a los llamadores]] - rationale - library/exceptions.py
- [[Exception]] - code
- [[F14 VAT RDT via download_report_content, decompress by compressionAlgorithm]] - rationale - REFACTORING.md
- [[F18 run_report raises on CANCELLEDFATAL terminal failure]] - rationale - REFACTORING.md
- [[F3 orders fallback only on HTTP 400 (not any error)]] - rationale - REFACTORING.md
- [[Fachada async de la SP-API agrupa Reports  Feeds  Tokens.  `AmazonClient` man]] - rationale - library/spapi_client.py
- [[FakeClient]] - code - tests/test_orders_fallback.py
- [[Feed processing (IN_QUEUE  IN_PROGRESS)]] - rationale - library/exceptions.py
- [[FeedDocumentResponse]] - code - library/models.py
- [[FeedStatusResponse]] - code - library/models.py
- [[Repite `check()` hasta que devuelva resultado (deja de lanzar exc_type),]] - rationale - library/spapi_client.py
- [[Report processing (IN_QUEUE  IN_PROGRESS)]] - rationale - library/exceptions.py
- [[ReportDocumentResponse]] - code - library/models.py
- [[ReportRun]] - code - library/models.py
- [[ReportStatusResponse]] - code - library/models.py
- [[Response]] - code
- [[RestrictedDataTokenResponse]] - code - library/models.py
- [[Resultado de la cadena create - poll - download de AmazonClient.run_report.]] - rationale - library/models.py
- [[TestOrdersFallback]] - code - tests/test_orders_fallback.py
- [[Tests del fallback de tipo de reporte en orders (_run_tsv).  Cubren el cambio de]] - rationale - tests/test_orders_fallback.py
- [[_run_tsv()]] - code - orders.py
- [[models.py]] - code - library/models.py
- [[pydantic==2.12.4]] - concept - requirements.txt
- [[spapi_client.py]] - code - library/spapi_client.py
- [[test_orders_fallback.py]] - code - tests/test_orders_fallback.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/SP-API_Exceptions
SORT file.name ASC
```

## Connections to other communities
- 14 edges to [[_COMMUNITY_Client Factory]]
- 12 edges to [[_COMMUNITY_Async Transport & Retry]]
- 7 edges to [[_COMMUNITY_Orders Module]]
- 5 edges to [[_COMMUNITY_Stock Module]]
- 4 edges to [[_COMMUNITY_Logging Helpers]]
- 3 edges to [[_COMMUNITY_Marketplace Catalog]]
- 2 edges to [[_COMMUNITY_LWA Token Provider]]
- 2 edges to [[_COMMUNITY_File IO]]
- 1 edge to [[_COMMUNITY_Stock Config]]
- 1 edge to [[_COMMUNITY_Runner & VAT]]
- 1 edge to [[_COMMUNITY_Async Migration (B1-B7)]]

## Top bridge nodes
- [[AmazonClient]] - degree 46, connects to 6 communities
- [[spapi_client.py]] - degree 25, connects to 6 communities
- [[AmazonAPIError]] - degree 24, connects to 3 communities
- [[AmazonReportNotReadyError]] - degree 11, connects to 3 communities
- [[AmazonFeedNotReadyError]] - degree 7, connects to 3 communities