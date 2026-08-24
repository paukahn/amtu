---
type: community
cohesion: 0.32
members: 8
---

# Logging Helpers

**Cohesion:** 0.32 - loosely connected
**Members:** 8 nodes

## Members
- [[.download_text()]] - code - library/spapi_client.py
- [[Funciones de logging del proyecto (info  error  debug + contexto).  Pase 2 la]] - rationale - library/logging_helpers/message_processor.py
- [[Imprime mensajes de depuración (solo en modo debug).      Args         message]] - rationale - library/logging_helpers/message_processor.py
- [[__init__.py_7]] - code - library/logging_helpers/__init__.py
- [[_ctx_record_factory()]] - code - library/logging_helpers/message_processor.py
- [[_ensure()]] - code - library/logging_helpers/message_processor.py
- [[debug()]] - code - library/logging_helpers/message_processor.py
- [[message_processor.py]] - code - library/logging_helpers/message_processor.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Logging_Helpers
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_SP-API Exceptions]]
- 3 edges to [[_COMMUNITY_Mailer]]
- 3 edges to [[_COMMUNITY_Stock Module]]
- 2 edges to [[_COMMUNITY_Common Config]]
- 2 edges to [[_COMMUNITY_Logging (Logger)]]
- 2 edges to [[_COMMUNITY_Runner & VAT]]
- 2 edges to [[_COMMUNITY_Async Transport & Retry]]

## Top bridge nodes
- [[message_processor.py]] - degree 10, connects to 5 communities
- [[_ensure()]] - degree 6, connects to 4 communities
- [[__init__.py_7]] - degree 5, connects to 3 communities
- [[debug()]] - degree 10, connects to 2 communities
- [[.download_text()]] - degree 2, connects to 1 community