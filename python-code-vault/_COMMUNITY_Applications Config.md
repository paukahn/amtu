---
type: community
cohesion: 0.09
members: 29
---

# Applications Config

**Cohesion:** 0.09 - loosely connected
**Members:** 29 nodes

## Members
- [[.__init__()_2]] - code - classes/config/Applications.py
- [[.__init__()_11]] - code - library/auth_provider.py
- [[.get_active_applications()]] - code - classes/config/Applications.py
- [[.get_active_applications_original()]] - code - classes/config/Applications.py
- [[.get_application()]] - code - classes/config/Applications.py
- [[.get_application_original()]] - code - classes/config/Applications.py
- [[.get_applications()]] - code - classes/config/Applications.py
- [[.get_applications_original()]] - code - classes/config/Applications.py
- [[.get_client_id()]] - code - classes/config/Applications.py
- [[.get_client_secret()]] - code - classes/config/Applications.py
- [[.is_enabled()]] - code - classes/config/Applications.py
- [[.set_enabled()]] - code - classes/config/Applications.py
- [[.test_acronym_and_amz_lowercased()]] - code - tests/test_orders_naming.py
- [[.test_already_lowercase_acronym()]] - code - tests/test_orders_naming.py
- [[.test_format_preserved()]] - code - tests/test_orders_naming.py
- [[.test_start_is_midnight()]] - code - tests/test_orders_naming.py
- [[.test_window_is_7_days_ending_now()]] - code - tests/test_orders_naming.py
- [[ApplicationsConfig]] - code - classes/config/Applications.py
- [[AsyncClient]] - code
- [[Credenciales LWA de las aplicaciones (applications.amzapps, cifrado).]] - rationale - classes/config/Applications.py
- [[Nombre del fichero local de pedidos acrónimo y 'amz' en MINÚSCULAS.      El con]] - rationale - orders.py
- [[Nombre del fichero local de pedidos acrónimo y 'amz' en minúsculas.  El consumi]] - rationale - tests/test_orders_naming.py
- [[TestLocalOutputName]] - code - tests/test_orders_naming.py
- [[TestOrdersDateRange]] - code - tests/test_orders_naming.py
- [[Ventana de pedidos del original desde las 0000 de hace 7 días hasta AHORA.]] - rationale - orders.py
- [[_local_output_name()]] - code - orders.py
- [[_orders_date_range()]] - code - orders.py
- [[test_orders_naming.py]] - code - tests/test_orders_naming.py
- [[timedelta]] - code

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Applications_Config
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_Orders Module]]
- 4 edges to [[_COMMUNITY_FTP Config]]
- 2 edges to [[_COMMUNITY_Config Save]]
- 2 edges to [[_COMMUNITY_Config Read]]
- 2 edges to [[_COMMUNITY_LWA Token Provider]]
- 1 edge to [[_COMMUNITY_Accounts Config]]
- 1 edge to [[_COMMUNITY_Stock Config]]
- 1 edge to [[_COMMUNITY_Acronyms Config]]
- 1 edge to [[_COMMUNITY_Runner & VAT]]

## Top bridge nodes
- [[ApplicationsConfig]] - degree 23, connects to 6 communities
- [[.__init__()_11]] - degree 5, connects to 2 communities
- [[_local_output_name()]] - degree 7, connects to 1 community
- [[_orders_date_range()]] - degree 7, connects to 1 community
- [[test_orders_naming.py]] - degree 6, connects to 1 community