---
type: community
cohesion: 0.50
members: 4
---

# DataTransformer Fixes

**Cohesion:** 0.50 - moderately connected
**Members:** 4 nodes

## Members
- [[B6 detect_separator got route not content]] - rationale - MIGRATION.md
- [[DataTransformer_1]] - code - REFACTORING.md
- [[F23e DataTransformer format_map only on config templates, never Amazon data]] - rationale - REFACTORING.md
- [[pandas==2.2.3]] - concept - requirements.txt

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/DataTransformer_Fixes
SORT file.name ASC
```
