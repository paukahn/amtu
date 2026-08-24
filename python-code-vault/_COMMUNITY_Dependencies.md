---
type: community
cohesion: 1.00
members: 2
---

# Dependencies

**Cohesion:** 1.00 - tightly connected
**Members:** 2 nodes

## Members
- [[requests removed (replaced by httpx with timeout)]] - rationale - REFACTORING.md
- [[requirements.txt runtime-only (devsecurity tools removed)]] - rationale - requirements.txt

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Dependencies
SORT file.name ASC
```
