---
source_file: "REFACTORING.md"
type: "rationale"
community: "LWA Token Provider"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/LWA_Token_Provider
---

# F19: to_thread config decrypt; force_refresh re-check under lock; _poll max(1,attempts); delete_token no secret leak

## Connections
- [[AsyncTokenProvider]] - `rationale_for` [INFERRED]
- [[B5 401 did not refresh token (only 429 handled)]] - `semantically_similar_to` [INFERRED]
- [[runner.py]] - `rationale_for` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/LWA_Token_Provider