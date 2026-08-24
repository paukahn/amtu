---
type: community
cohesion: 0.20
members: 16
---

# DataTransformer (SAP)

**Cohesion:** 0.20 - loosely connected
**Members:** 16 nodes

## Members
- [[.__init__()_4]] - code - classes/config/DataTransformer.py
- [[._apply_logic()]] - code - classes/config/DataTransformer.py
- [[._expand_template()]] - code - classes/config/DataTransformer.py
- [[._get_region_data()]] - code - classes/config/DataTransformer.py
- [[._load_config()]] - code - classes/config/DataTransformer.py
- [[.test_amazon_data_with_braces_is_not_formatted()]] - code - tests/test_datatransformer.py
- [[.test_bad_config_template_does_not_crash()]] - code - tests/test_datatransformer.py
- [[.test_config_logic_template_is_expanded()]] - code - tests/test_datatransformer.py
- [[.test_format_string_injection_is_inert()]] - code - tests/test_datatransformer.py
- [[.transform()]] - code - classes/config/DataTransformer.py
- [[DataTransformer]] - code - classes/config/DataTransformer.py
- [[DataTransformer._apply_logic format_map SOLO sobre plantillas de config.  Antes]] - rationale - tests/test_datatransformer.py
- [[Expande una plantilla de CONFIG con context_vars + fila.          Tolera plant]] - rationale - classes/config/DataTransformer.py
- [[TestApplyLogicFormatMap]] - code - tests/test_datatransformer.py
- [[_make_transformer()]] - code - tests/test_datatransformer.py
- [[test_datatransformer.py]] - code - tests/test_datatransformer.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/DataTransformer_SAP
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_Acronyms Config]]
- 1 edge to [[_COMMUNITY_Orders Module]]

## Top bridge nodes
- [[DataTransformer]] - degree 12, connects to 2 communities
- [[.__init__()_4]] - degree 4, connects to 1 community
- [[test_datatransformer.py]] - degree 4, connects to 1 community