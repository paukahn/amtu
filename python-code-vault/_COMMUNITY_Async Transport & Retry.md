---
type: community
cohesion: 0.10
members: 45
---

# Async Transport & Retry

**Cohesion:** 0.10 - loosely connected
**Members:** 45 nodes

## Members
- [[.__init__()_16]] - code - library/transport.py
- [[.__init__()_20]] - code - tests/test_transport.py
- [[._do_request()]] - code - library/transport.py
- [[._log_debug()]] - code - library/transport.py
- [[.request()]] - code - library/transport.py
- [[.test_200_ok_calls_limiter_and_returns()]] - code - tests/test_transport.py
- [[.test_401_raises_auth_and_is_not_retried()]] - code - tests/test_transport.py
- [[.test_429_then_200_is_retried()]] - code - tests/test_transport.py
- [[.test_500_then_200_is_retried()]] - code - tests/test_transport.py
- [[.test_handles_spaces_around_colon()]] - code - tests/test_redaction.py
- [[.test_network_error_then_200_is_retried()]] - code - tests/test_transport.py
- [[.test_non_sensitive_body_unchanged()]] - code - tests/test_redaction.py
- [[.test_persistent_429_raises_throttle()]] - code - tests/test_transport.py
- [[.test_persistent_500_raises_server_error()]] - code - tests/test_transport.py
- [[.test_quota_exceeded_in_body_is_throttled()]] - code - tests/test_transport.py
- [[.test_redacts_presigned_url()]] - code - tests/test_redaction.py
- [[.test_redacts_restricted_data_token()]] - code - tests/test_redaction.py
- [[.update()_1]] - code - tests/test_transport.py
- [[.wait()_1]] - code - tests/test_transport.py
- [[AmazonAuthError]] - code - library/exceptions.py
- [[AmazonServerError]] - code - library/exceptions.py
- [[AmazonThrottleError]] - code - library/exceptions.py
- [[AsyncClient_1]] - code
- [[AsyncTransport]] - code - library/transport.py
- [[B7 no request timeouts (except auth refresh)]] - rationale - MIGRATION.md
- [[Capa de transporte async para la SP-API.  Una sola corrutina `request()` concent]] - rationale - library/transport.py
- [[Error 401 (Unauthorized)]] - rationale - library/exceptions.py
- [[Error 429  Quota Exceeded]] - rationale - library/exceptions.py
- [[Error 5xx de la SP-API (transitorio se reintenta en el transporte)]] - rationale - library/exceptions.py
- [[F23b _log_debug redacts response body (RDT, pre-signed S3 URL)]] - rationale - REFACTORING.md
- [[F4 transport retries 5xx and network errors]] - rationale - REFACTORING.md
- [[FakeLimiter]] - code - tests/test_transport.py
- [[Redacción de secretos en el log de debug del transporte.  El cuerpo de respuesta]] - rationale - tests/test_redaction.py
- [[Response_1]] - code
- [[TestRedactBody]] - code - tests/test_redaction.py
- [[TestTransport]] - code - tests/test_transport.py
- [[Tests de AsyncTransport con httpx.MockTransport (sin red real).]] - rationale - tests/test_transport.py
- [[_redact_body()]] - code - library/transport.py
- [[exceptions.py]] - code - library/exceptions.py
- [[httpx==0.28.1]] - concept - requirements.txt
- [[make_client()]] - code - tests/test_transport.py
- [[tenacity==9.1.2]] - concept - requirements.txt
- [[test_redaction.py]] - code - tests/test_redaction.py
- [[test_transport.py]] - code - tests/test_transport.py
- [[transport.py]] - code - library/transport.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Async_Transport__Retry
SORT file.name ASC
```

## Connections to other communities
- 12 edges to [[_COMMUNITY_SP-API Exceptions]]
- 12 edges to [[_COMMUNITY_Client Factory]]
- 3 edges to [[_COMMUNITY_Runner & VAT]]
- 2 edges to [[_COMMUNITY_Orders Module]]
- 2 edges to [[_COMMUNITY_Stock Module]]
- 2 edges to [[_COMMUNITY_File IO]]
- 2 edges to [[_COMMUNITY_Logging Helpers]]

## Top bridge nodes
- [[exceptions.py]] - degree 15, connects to 6 communities
- [[AmazonThrottleError]] - degree 13, connects to 5 communities
- [[AsyncTransport]] - degree 34, connects to 3 communities
- [[transport.py]] - degree 13, connects to 3 communities
- [[AmazonAuthError]] - degree 11, connects to 1 community