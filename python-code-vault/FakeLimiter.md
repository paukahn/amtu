---
source_file: "tests/test_transport.py"
type: "code"
community: "Async Transport & Retry"
location: "L16"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Async_Transport__Retry
---

# FakeLimiter

## Connections
- [[.__init__()_20]] - `method` [EXTRACTED]
- [[.test_200_ok_calls_limiter_and_returns()]] - `calls` [EXTRACTED]
- [[.test_401_raises_auth_and_is_not_retried()]] - `calls` [EXTRACTED]
- [[.test_429_then_200_is_retried()]] - `calls` [EXTRACTED]
- [[.test_500_then_200_is_retried()]] - `calls` [EXTRACTED]
- [[.test_network_error_then_200_is_retried()]] - `calls` [EXTRACTED]
- [[.test_persistent_429_raises_throttle()]] - `calls` [EXTRACTED]
- [[.test_persistent_500_raises_server_error()]] - `calls` [EXTRACTED]
- [[.test_quota_exceeded_in_body_is_throttled()]] - `calls` [EXTRACTED]
- [[.update()_1]] - `method` [EXTRACTED]
- [[.wait()_1]] - `method` [EXTRACTED]
- [[AmazonAuthError]] - `uses` [INFERRED]
- [[AmazonServerError]] - `uses` [INFERRED]
- [[AmazonThrottleError]] - `uses` [INFERRED]
- [[AsyncTransport]] - `uses` [INFERRED]
- [[test_transport.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Async_Transport__Retry