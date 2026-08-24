---
type: community
cohesion: 0.06
members: 52
---

# Client Factory

**Cohesion:** 0.06 - loosely connected
**Members:** 52 nodes

## Members
- [[.__aenter__()]] - code - library/factory.py
- [[.__aexit__()]] - code - library/factory.py
- [[.__init__()_13]] - code - library/factory.py
- [[.__init__()_14]] - code - library/rate_limiter.py
- [[.__init__()_17]] - code - tests/test_client.py
- [[.__init__()_18]] - code - tests/test_factory_debug.py
- [[._key()]] - code - library/rate_limiter.py
- [[.aclose()]] - code - library/factory.py
- [[.client()]] - code - library/factory.py
- [[.get_access_token()_1]] - code - tests/test_client.py
- [[.get_base_delay()_1]] - code - tests/test_client.py
- [[.get_factor()_1]] - code - tests/test_client.py
- [[.get_jitter()_1]] - code - tests/test_client.py
- [[.get_max_attempts()_1]] - code - tests/test_client.py
- [[.get_max_delay()_1]] - code - tests/test_client.py
- [[.test_401_triggers_refresh_and_retry()]] - code - tests/test_client.py
- [[.test_debug_defaults_to_false()]] - code - tests/test_factory_debug.py
- [[.test_debug_flag_reaches_transport()]] - code - tests/test_factory_debug.py
- [[.test_no_rate_means_no_sleep()]] - code - tests/test_rate_limiter.py
- [[.test_report_status_polls_until_terminal()]] - code - tests/test_client.py
- [[.test_run_report_decompresses_gzip_document()]] - code - tests/test_client.py
- [[.test_run_report_full_chain_plain_document()]] - code - tests/test_client.py
- [[.test_run_report_raises_on_terminal_failure()]] - code - tests/test_client.py
- [[.test_run_report_without_document_returns_empty_content()]] - code - tests/test_client.py
- [[.test_send_tracking_feed_raises_when_s3_put_fails()]] - code - tests/test_client.py
- [[.test_throttles_after_burst_is_drained()]] - code - tests/test_rate_limiter.py
- [[.test_update_ignores_missing_or_invalid_header()]] - code - tests/test_rate_limiter.py
- [[.update()]] - code - library/rate_limiter.py
- [[.wait()]] - code - library/rate_limiter.py
- [[AccountClients]] - code - library/factory.py
- [[Actualiza el rate desde la cabecera de respuesta de Amazon.          Es síncrono]] - rationale - library/rate_limiter.py
- [[Async rate limiter for the Amazon SP-API (token-bucket per regionendpoint).  Re]] - rationale - library/rate_limiter.py
- [[AsyncTokenBucket]] - code - library/rate_limiter.py
- [[B1 rate-limiter no-op (read _rates not _last_call)]] - rationale - MIGRATION.md
- [[El flag `debug` debe fluir AccountClients - AsyncTransport.  Regresión en modo]] - rationale - tests/test_factory_debug.py
- [[Factory ensambla los recursos async de una cuenta y produce AmazonClient.  Reem]] - rationale - library/factory.py
- [[FakePolling]] - code - tests/test_client.py
- [[FakeTokens]] - code - tests/test_client.py
- [[Handler que responde la cadena completa create-status-RDT-doc-S3.]] - rationale - tests/test_client.py
- [[TestClient]] - code - tests/test_client.py
- [[TestFactoryDebugFlag]] - code - tests/test_factory_debug.py
- [[TestRateLimiter]] - code - tests/test_rate_limiter.py
- [[Tests de AmazonClient polling, refresh-on-401 y run_report, con fakes.]] - rationale - tests/test_client.py
- [[Tests del token-bucket async (corrige B1 el limiter original nunca dormía).  No]] - rationale - tests/test_rate_limiter.py
- [[_FakeTokenProvider]] - code - tests/test_factory_debug.py
- [[build_client()]] - code - tests/test_client.py
- [[factory.py]] - code - library/factory.py
- [[rate_limiter.py]] - code - library/rate_limiter.py
- [[report_chain_handler()]] - code - tests/test_client.py
- [[test_client.py]] - code - tests/test_client.py
- [[test_factory_debug.py]] - code - tests/test_factory_debug.py
- [[test_rate_limiter.py]] - code - tests/test_rate_limiter.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Client_Factory
SORT file.name ASC
```

## Connections to other communities
- 14 edges to [[_COMMUNITY_SP-API Exceptions]]
- 12 edges to [[_COMMUNITY_Async Transport & Retry]]
- 4 edges to [[_COMMUNITY_LWA Token Provider]]
- 3 edges to [[_COMMUNITY_Runner & VAT]]

## Top bridge nodes
- [[factory.py]] - degree 12, connects to 4 communities
- [[AccountClients]] - degree 12, connects to 4 communities
- [[test_client.py]] - degree 14, connects to 2 communities
- [[build_client()]] - degree 13, connects to 2 communities
- [[TestClient]] - degree 12, connects to 2 communities