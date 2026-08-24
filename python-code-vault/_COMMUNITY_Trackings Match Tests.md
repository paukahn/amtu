---
type: community
cohesion: 0.31
members: 10
---

# Trackings Match Tests

**Cohesion:** 0.31 - loosely connected
**Members:** 10 nodes

## Members
- [[.test_does_not_match_other_account()]] - code - tests/test_trackings_match.py
- [[.test_lowercase_acronym_too()]] - code - tests/test_trackings_match.py
- [[.test_lowercase_file_uppercase_acronym()]] - code - tests/test_trackings_match.py
- [[.test_requires_underscore_separator()]] - code - tests/test_trackings_match.py
- [[.test_uppercase_file_uppercase_acronym()]] - code - tests/test_trackings_match.py
- [[Match de fichero de trackings por acrónimo, sin distinguir mayúsculas.  Regresió]] - rationale - tests/test_trackings_match.py
- [[TestBelongsToAcronym]] - code - tests/test_trackings_match.py
- [[_belongs_to_acronym()]] - code - trackings.py
- [[test_trackings_match.py]] - code - tests/test_trackings_match.py
- [[¿El fichero pertenece a esta cuenta Prefijo `acronimo_` SIN distinguir     mayú]] - rationale - trackings.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Trackings_Match_Tests
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_File IO]]
- 1 edge to [[_COMMUNITY_Marketplace Catalog]]

## Top bridge nodes
- [[_belongs_to_acronym()]] - degree 9, connects to 2 communities
- [[test_trackings_match.py]] - degree 4, connects to 1 community