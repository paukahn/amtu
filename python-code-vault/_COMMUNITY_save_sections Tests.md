---
type: community
cohesion: 0.47
members: 6
---

# save_sections Tests

**Cohesion:** 0.47 - moderately connected
**Members:** 6 nodes

## Members
- [[._read()]] - code - tests/test_config_base.py
- [[.setUp()_2]] - code - tests/test_config_base.py
- [[.tearDown()_2]] - code - tests/test_config_base.py
- [[.test_default_filters_empty_values_and_sections()]] - code - tests/test_config_base.py
- [[.test_keep_empty_preserves_blank_fields()]] - code - tests/test_config_base.py
- [[TestSaveSections]] - code - tests/test_config_base.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/save_sections_Tests
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Config Save]]
- 1 edge to [[_COMMUNITY_Stock Config]]

## Top bridge nodes
- [[TestSaveSections]] - degree 7, connects to 2 communities
- [[.test_default_filters_empty_values_and_sections()]] - degree 3, connects to 1 community
- [[.test_keep_empty_preserves_blank_fields()]] - degree 3, connects to 1 community