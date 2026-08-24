---
source_file: "library/transport.py"
type: "code"
community: "Async Transport & Retry"
location: "L63"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Async_Transport__Retry
---

# AsyncTransport

## Connections
- [[.__init__()_13]] - `calls` [EXTRACTED]
- [[.__init__()_16]] - `method` [EXTRACTED]
- [[._do_request()]] - `method` [EXTRACTED]
- [[._log_debug()]] - `method` [EXTRACTED]
- [[.request()]] - `method` [EXTRACTED]
- [[.test_200_ok_calls_limiter_and_returns()]] - `calls` [EXTRACTED]
- [[.test_401_raises_auth_and_is_not_retried()]] - `calls` [EXTRACTED]
- [[.test_429_then_200_is_retried()]] - `calls` [EXTRACTED]
- [[.test_500_then_200_is_retried()]] - `calls` [EXTRACTED]
- [[.test_network_error_then_200_is_retried()]] - `calls` [EXTRACTED]
- [[.test_persistent_429_raises_throttle()]] - `calls` [EXTRACTED]
- [[.test_persistent_500_raises_server_error()]] - `calls` [EXTRACTED]
- [[.test_quota_exceeded_in_body_is_throttled()]] - `calls` [EXTRACTED]
- [[AccountClients]] - `uses` [INFERRED]
- [[AmazonAuthError]] - `uses` [INFERRED]
- [[AmazonClient]] - `calls` [EXTRACTED]
- [[AmazonServerError]] - `uses` [INFERRED]
- [[AmazonThrottleError]] - `uses` [INFERRED]
- [[AsyncTokenBucket]] - `calls` [INFERRED]
- [[B7 no request timeouts (except auth refresh)]] - `rationale_for` [EXTRACTED]
- [[F15 debug mode restored (runner derives debug - AccountClients - AsyncTransport)]] - `rationale_for` [EXTRACTED]
- [[F23b _log_debug redacts response body (RDT, pre-signed S3 URL)]] - `rationale_for` [EXTRACTED]
- [[F4 transport retries 5xx and network errors]] - `rationale_for` [EXTRACTED]
- [[FakeLimiter]] - `uses` [INFERRED]
- [[FakePolling]] - `uses` [INFERRED]
- [[FakeTokens]] - `uses` [INFERRED]
- [[TestClient]] - `uses` [INFERRED]
- [[TestTransport]] - `uses` [INFERRED]
- [[build_client()]] - `calls` [EXTRACTED]
- [[factory.py]] - `imports` [EXTRACTED]
- [[httpx==0.28.1]] - `references` [INFERRED]
- [[test_client.py]] - `imports` [EXTRACTED]
- [[test_transport.py]] - `imports` [EXTRACTED]
- [[transport.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Async_Transport__Retry