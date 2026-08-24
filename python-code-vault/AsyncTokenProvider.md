---
source_file: "library/auth_provider.py"
type: "code"
community: "LWA Token Provider"
location: "L93"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/LWA_Token_Provider
---

# AsyncTokenProvider

## Connections
- [[.__init__()_11]] - `method` [EXTRACTED]
- [[.__init__()_13]] - `calls` [EXTRACTED]
- [[._cache_path()]] - `method` [EXTRACTED]
- [[._lock()]] - `method` [EXTRACTED]
- [[._refresh()]] - `method` [EXTRACTED]
- [[._valid_token()]] - `method` [EXTRACTED]
- [[.get_access_token()]] - `method` [EXTRACTED]
- [[AccountClients]] - `uses` [INFERRED]
- [[AmazonClient]] - `calls` [INFERRED]
- [[F17 quota-in-body AmazonThrottleError carries statusbody; atomic token cache (os.replace)]] - `rationale_for` [INFERRED]
- [[F19 to_thread config decrypt; force_refresh re-check under lock; _poll max(1,attempts); delete_token no secret leak]] - `rationale_for` [INFERRED]
- [[F23a access-token cache encrypted at rest (AES+HMAC via data_protector)]] - `rationale_for` [INFERRED]
- [[F5 access-token cache using LWA expires_in (JSON expires_at)]] - `rationale_for` [EXTRACTED]
- [[F6 LWA refresh retried 3x on network5xx]] - `rationale_for` [EXTRACTED]
- [[_warm_account()]] - `calls` [EXTRACTED]
- [[auth_provider.py]] - `contains` [EXTRACTED]
- [[factory.py]] - `imports` [EXTRACTED]
- [[main.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/LWA_Token_Provider