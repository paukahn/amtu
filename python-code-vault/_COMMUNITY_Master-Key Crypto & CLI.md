---
type: community
cohesion: 0.13
members: 26
---

# Master-Key Crypto & CLI

**Cohesion:** 0.13 - loosely connected
**Members:** 26 nodes

## Members
- [[.setUp()_3]] - code - tests/test_crypto_utils.py
- [[.tearDown()_3]] - code - tests/test_crypto_utils.py
- [[.test_legacy_v1_still_loads()]] - code - tests/test_crypto_utils.py
- [[.test_v2_roundtrip()]] - code - tests/test_crypto_utils.py
- [[.test_v2_tamper_detected()]] - code - tests/test_crypto_utils.py
- [[.test_v2_wrong_password_rejected()]] - code - tests/test_crypto_utils.py
- [[Cifrado de la llave maestra en secret_keys.bin (ruta CLI con contraseña).  Forma]] - rationale - library/security/crypto_utils.py
- [[Devuelve (key, hmac_key).      - auto=True  → intenta leer .env.secret en bina]] - rationale - library/security/key_manager.py
- [[Devuelve (key, hmac_key). Lee v2 (autenticado) y, por compatibilidad, v1.]] - rationale - library/security/crypto_utils.py
- [[TestCryptoUtils]] - code - tests/test_crypto_utils.py
- [[__init__.py_8]] - code - library/security/__init__.py
- [[_derive_v1()]] - code - library/security/crypto_utils.py
- [[_derive_v2()]] - code - library/security/crypto_utils.py
- [[_load_v1()]] - code - library/security/crypto_utils.py
- [[_load_v2()]] - code - library/security/crypto_utils.py
- [[app_control.py]] - code - app_control.py
- [[crypto_utils.py]] - code - library/security/crypto_utils.py
- [[encrypt_keys()]] - code - library/security/crypto_utils.py
- [[key_manager.py]] - code - library/security/key_manager.py
- [[load_keys()]] - code - library/security/crypto_utils.py
- [[load_keys()_1]] - code - library/security/key_manager.py
- [[load_master_keys()]] - code - library/security/key_manager.py
- [[pad()]] - code - library/security/crypto_utils.py
- [[secret_keys.bin formato v2 (PBKDF2-SHA256600k + Encrypt-then-MAC) + compat v1.]] - rationale - tests/test_crypto_utils.py
- [[test_crypto_utils.py]] - code - tests/test_crypto_utils.py
- [[unpad()]] - code - library/security/crypto_utils.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Master-Key_Crypto__CLI
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_FTP Config]]
- 4 edges to [[_COMMUNITY_Mailer]]
- 2 edges to [[_COMMUNITY_Runner & VAT]]
- 2 edges to [[_COMMUNITY_LWA Token Provider]]
- 1 edge to [[_COMMUNITY_Stock Config]]

## Top bridge nodes
- [[load_master_keys()]] - degree 10, connects to 3 communities
- [[app_control.py]] - degree 4, connects to 2 communities
- [[__init__.py_8]] - degree 8, connects to 1 community
- [[load_keys()_1]] - degree 7, connects to 1 community
- [[encrypt_keys()]] - degree 6, connects to 1 community