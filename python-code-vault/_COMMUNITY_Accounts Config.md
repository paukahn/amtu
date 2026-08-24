---
type: community
cohesion: 0.27
members: 10
---

# Accounts Config

**Cohesion:** 0.27 - loosely connected
**Members:** 10 nodes

## Members
- [[.__init__()]] - code - classes/config/Accounts.py
- [[.accounts_list()]] - code - classes/config/Accounts.py
- [[.get_account()]] - code - classes/config/Accounts.py
- [[.get_accounts_by_application()]] - code - classes/config/Accounts.py
- [[.get_all_accounts()]] - code - classes/config/Accounts.py
- [[.get_application_name_for_account()]] - code - classes/config/Accounts.py
- [[.load_accounts()]] - code - classes/config/Accounts.py
- [[Accounts.py]] - code - classes/config/Accounts.py
- [[AccountsConfig]] - code - classes/config/Accounts.py
- [[Cuentas de vendedor (accounts.ini).      Ya no es singleton cada construcción r]] - rationale - classes/config/Accounts.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Accounts_Config
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Config Save]]
- 3 edges to [[_COMMUNITY_Stock Config]]
- 3 edges to [[_COMMUNITY_LWA Token Provider]]
- 2 edges to [[_COMMUNITY_Config Parser (base)]]
- 2 edges to [[_COMMUNITY_Config Read]]
- 2 edges to [[_COMMUNITY_Acronyms Config]]
- 2 edges to [[_COMMUNITY_Runner & VAT]]
- 1 edge to [[_COMMUNITY_Applications Config]]

## Top bridge nodes
- [[AccountsConfig]] - degree 17, connects to 5 communities
- [[Accounts.py]] - degree 7, connects to 5 communities
- [[.load_accounts()]] - degree 6, connects to 4 communities