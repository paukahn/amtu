---
type: community
cohesion: 1.00
members: 1
---

# Orders date window (F27)

**Cohesion:** 1.00 - tightly connected
**Members:** 1 nodes

## Members
- [[F27 orders 7-day date window (0000 seven days ago - now)]] - rationale - REFACTORING.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Orders_date_window_F27
SORT file.name ASC
```
