---
type: community
cohesion: 0.67
members: 3
---

# Case-Sensitivity Fixes

**Cohesion:** 0.67 - moderately connected
**Members:** 3 nodes

## Members
- [[Account acronym cosmic - COS]] - concept - config/acronyms.txt
- [[F25 trackings acronym file match case-insensitive (_belongs_to_acronym)]] - rationale - REFACTORING.md
- [[F26 orders local file uses lowercase acronym+amz ({id}_cos_amz.txt)]] - rationale - REFACTORING.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Case-Sensitivity_Fixes
SORT file.name ASC
```
