---
type: community
cohesion: 0.18
members: 11
---

# Async Migration (B1-B7)

**Cohesion:** 0.18 - loosely connected
**Members:** 11 nodes

## Members
- [[Async refactor of SP-API integration]] - concept - MIGRATION.md
- [[B3 .env.secret hex vs 64 raw bytes mismatch]] - rationale - MIGRATION.md
- [[B4 dead enrich_feed_with_product_types removed]] - rationale - MIGRATION.md
- [[Call chain module - AmazonClient - AsyncTransport - httpx.AsyncClient]] - concept - MIGRATION.md
- [[F11 brand_analytics module removed (never worked, optional)]] - rationale - REFACTORING.md
- [[F23a access-token cache encrypted at rest (AES+HMAC via data_protector)]] - rationale - REFACTORING.md
- [[F24a secret_keys.bin crypto v2 (PBKDF2-SHA256600k + Encrypt-then-MAC), v1 migration]] - rationale - REFACTORING.md
- [[Refactor without observable behavior change (pass 1)]] - rationale - MIGRATION.md
- [[asyncio.to_thread for blocking ops (pandasfilesSMTPFTP)]] - rationale - MIGRATION.md
- [[data_protector (AES+HMAC encryption helper)]] - code - REFACTORING.md
- [[pycryptodome==3.23.0]] - concept - requirements.txt

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Async_Migration_B1-B7
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_LWA Token Provider]]
- 1 edge to [[_COMMUNITY_SP-API Exceptions]]

## Top bridge nodes
- [[Call chain module - AmazonClient - AsyncTransport - httpx.AsyncClient]] - degree 2, connects to 1 community
- [[F23a access-token cache encrypted at rest (AES+HMAC via data_protector)]] - degree 2, connects to 1 community