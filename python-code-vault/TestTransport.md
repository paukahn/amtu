---
source_file: "tests/test_transport.py"
type: "code"
community: "Async Transport & Retry"
location: "L28"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Async_Transport__Retry
---

# TestTransport

## Connections
- [[.test_200_ok_calls_limiter_and_returns()]] - `method` [EXTRACTED]
- [[.test_401_raises_auth_and_is_not_retried()]] - `method` [EXTRACTED]
- [[.test_429_then_200_is_retried()]] - `method` [EXTRACTED]
- [[.test_500_then_200_is_retried()]] - `method` [EXTRACTED]
- [[.test_network_error_then_200_is_retried()]] - `method` [EXTRACTED]
- [[.test_persistent_429_raises_throttle()]] - `method` [EXTRACTED]
- [[.test_persistent_500_raises_server_error()]] - `method` [EXTRACTED]
- [[.test_quota_exceeded_in_body_is_throttled()]] - `method` [EXTRACTED]
- [[AmazonAuthError]] - `uses` [INFERRED]
- [[AmazonServerError]] - `uses` [INFERRED]
- [[AmazonThrottleError]] - `uses` [INFERRED]
- [[AsyncTransport]] - `uses` [INFERRED]
- [[test_transport.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Async_Transport__Retry