---
source_file: "REFACTORING.md"
type: "rationale"
community: "Async Migration (B1-B7)"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Async_Migration_B1-B7
---

# F24a: secret_keys.bin crypto v2 (PBKDF2-SHA256/600k + Encrypt-then-MAC), v1 migration

## Connections
- [[B3 .env.secret hex vs 64 raw bytes mismatch]] - `semantically_similar_to` [INFERRED]
- [[data_protector (AES+HMAC encryption helper)]] - `rationale_for` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Async_Migration_B1-B7