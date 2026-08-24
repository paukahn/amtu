---
type: community
cohesion: 0.08
members: 41
---

# LWA Token Provider

**Cohesion:** 0.08 - loosely connected
**Members:** 41 nodes

## Members
- [[._cache_path()]] - code - library/auth_provider.py
- [[._lock()]] - code - library/auth_provider.py
- [[._refresh()]] - code - library/auth_provider.py
- [[._valid_token()]] - code - library/auth_provider.py
- [[.get_access_token()]] - code - library/auth_provider.py
- [[.setUp()_1]] - code - tests/test_auth_cache.py
- [[.setUp()]] - code - tests/test_auth_cache.py
- [[.tearDown()_1]] - code - tests/test_auth_cache.py
- [[.tearDown()]] - code - tests/test_auth_cache.py
- [[.test_corrupt_json_is_expired()]] - code - tests/test_auth_cache.py
- [[.test_encrypted_roundtrip()]] - code - tests/test_auth_cache.py
- [[.test_legacy_plaintext_file_is_expired()]] - code - tests/test_auth_cache.py
- [[.test_legacy_plaintext_read_with_keys_is_expired()]] - code - tests/test_auth_cache.py
- [[.test_missing_file()]] - code - tests/test_auth_cache.py
- [[.test_respects_safety_margin()]] - code - tests/test_auth_cache.py
- [[.test_roundtrip()]] - code - tests/test_auth_cache.py
- [[.test_wrong_key_is_expired()]] - code - tests/test_auth_cache.py
- [[AsyncTokenProvider]] - code - library/auth_provider.py
- [[B5 401 did not refresh token (only 429 handled)]] - rationale - MIGRATION.md
- [[BaseException]] - code
- [[Devuelve (token, expires_at).      Con keyhmac_key el fichero se descifra (AES+]] - rationale - library/auth_provider.py
- [[F17 quota-in-body AmazonThrottleError carries statusbody; atomic token cache (os.replace)]] - rationale - REFACTORING.md
- [[F19 to_thread config decrypt; force_refresh re-check under lock; _poll max(1,attempts); delete_token no secret leak]] - rationale - REFACTORING.md
- [[F5 access-token cache using LWA expires_in (JSON expires_at)]] - rationale - REFACTORING.md
- [[F6 LWA refresh retried 3x on network5xx]] - rationale - REFACTORING.md
- [[Lock]] - code
- [[Proveedor de tokens async para LWA (Login With Amazon).  Mismo papel que en el p]] - rationale - library/auth_provider.py
- [[Smoke-test de tokens refrescaimprime el access token de cada cuenta-mercado.]] - rationale - main.py
- [[TestEncryptedTokenCache]] - code - tests/test_auth_cache.py
- [[TestStillValid]] - code - tests/test_auth_cache.py
- [[TestTokenCache]] - code - tests/test_auth_cache.py
- [[Tests de la caché de access tokens por expires_in (libraryauth_provider.py).  C]] - rationale - tests/test_auth_cache.py
- [[_is_transient_lwa_error()]] - code - library/auth_provider.py
- [[_main()]] - code - main.py
- [[_read_cache()]] - code - library/auth_provider.py
- [[_still_valid()]] - code - library/auth_provider.py
- [[_warm_account()]] - code - main.py
- [[_write_cache()]] - code - library/auth_provider.py
- [[auth_provider.py]] - code - library/auth_provider.py
- [[main.py]] - code - main.py
- [[test_auth_cache.py]] - code - tests/test_auth_cache.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/LWA_Token_Provider
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_FTP Config]]
- 4 edges to [[_COMMUNITY_Client Factory]]
- 3 edges to [[_COMMUNITY_Accounts Config]]
- 3 edges to [[_COMMUNITY_Mailer]]
- 2 edges to [[_COMMUNITY_Applications Config]]
- 2 edges to [[_COMMUNITY_SP-API Exceptions]]
- 2 edges to [[_COMMUNITY_Stock Module]]
- 2 edges to [[_COMMUNITY_Master-Key Crypto & CLI]]
- 1 edge to [[_COMMUNITY_Async Migration (B1-B7)]]
- 1 edge to [[_COMMUNITY_Runner & VAT]]

## Top bridge nodes
- [[AsyncTokenProvider]] - degree 18, connects to 4 communities
- [[auth_provider.py]] - degree 13, connects to 4 communities
- [[main.py]] - degree 9, connects to 4 communities
- [[_main()]] - degree 5, connects to 3 communities
- [[_warm_account()]] - degree 5, connects to 2 communities