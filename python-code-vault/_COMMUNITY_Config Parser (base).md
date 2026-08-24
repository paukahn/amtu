---
type: community
cohesion: 0.29
members: 12
---

# Config Parser (base)

**Cohesion:** 0.29 - loosely connected
**Members:** 12 nodes

## Members
- [[.test_basic_sections_and_pairs()]] - code - tests/test_config_base.py
- [[.test_block_comments_toggle()]] - code - tests/test_config_base.py
- [[.test_duplicate_keys_are_preserved_in_order()]] - code - tests/test_config_base.py
- [[.test_duplicate_sections_are_merged()]] - code - tests/test_config_base.py
- [[.test_full_line_comment_skipped_when_inline_disabled()]] - code - tests/test_config_base.py
- [[.test_hash_preserved_in_values_when_inline_disabled()]] - code - tests/test_config_base.py
- [[.test_inline_comments_stripped_when_enabled()]] - code - tests/test_config_base.py
- [[.test_malformed_line_reported_and_skipped()]] - code - tests/test_config_base.py
- [[.test_section_names_keep_original_case()]] - code - tests/test_config_base.py
- [[Parsea texto tipo INI a {sección (clave, valor), ...}.      - Los nombres de]] - rationale - classes/config/base.py
- [[TestParseSections]] - code - tests/test_config_base.py
- [[parse_sections()]] - code - classes/config/base.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Config_Parser_base
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_Config Save]]
- 3 edges to [[_COMMUNITY_Stock Config]]
- 2 edges to [[_COMMUNITY_Accounts Config]]
- 2 edges to [[_COMMUNITY_Config Read]]
- 2 edges to [[_COMMUNITY_Polling Config]]

## Top bridge nodes
- [[parse_sections()]] - degree 22, connects to 5 communities
- [[TestParseSections]] - degree 11, connects to 2 communities