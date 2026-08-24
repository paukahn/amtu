---
source_file: "library/rate_limiter.py"
type: "code"
community: "Client Factory"
location: "L22"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Client_Factory
---

# AsyncTokenBucket

## Connections
- [[.__init__()_13]] - `calls` [EXTRACTED]
- [[.__init__()_14]] - `method` [EXTRACTED]
- [[._key()]] - `method` [EXTRACTED]
- [[.test_no_rate_means_no_sleep()]] - `calls` [EXTRACTED]
- [[.test_throttles_after_burst_is_drained()]] - `calls` [EXTRACTED]
- [[.test_update_ignores_missing_or_invalid_header()]] - `calls` [EXTRACTED]
- [[.update()]] - `method` [EXTRACTED]
- [[.wait()]] - `method` [EXTRACTED]
- [[AccountClients]] - `uses` [INFERRED]
- [[AsyncTransport]] - `calls` [INFERRED]
- [[B1 rate-limiter no-op (read _rates not _last_call)]] - `rationale_for` [EXTRACTED]
- [[FakePolling]] - `uses` [INFERRED]
- [[FakeTokens]] - `uses` [INFERRED]
- [[TestClient]] - `uses` [INFERRED]
- [[TestRateLimiter]] - `uses` [INFERRED]
- [[build_client()]] - `calls` [EXTRACTED]
- [[factory.py]] - `imports` [EXTRACTED]
- [[rate_limiter.py]] - `contains` [EXTRACTED]
- [[test_client.py]] - `imports` [EXTRACTED]
- [[test_rate_limiter.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Client_Factory