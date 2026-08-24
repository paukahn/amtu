---
type: community
cohesion: 0.13
members: 22
---

# File I/O

**Cohesion:** 0.13 - loosely connected
**Members:** 22 nodes

## Members
- [[Borra el TSV temporal cuando el envío del feed falló (no llega a archivarse).]] - rationale - trackings.py
- [[DataFrame]] - code
- [[Descomprime un blob gzip a texto.]] - rationale - library/helper_functions.py
- [[Detecta automáticamente si el contenido está separado por tabulaciones o comas u]] - rationale - library/file_explorer.py
- [[ES de ficheros locales y remotos de los módulos.  Cambios del pase 2 - Sin sid]] - rationale - library/file_explorer.py
- [[Guarda los datos del reporte fiscal (ya procesados) en un archivo TSV     bajo]] - rationale - library/file_explorer.py
- [[Lee archivo remoto (CSV o TSV) detectando automáticamente el separador.     BLOQ]] - rationale - library/file_explorer.py
- [[Módulo de trackings feed POST_FLAT_FILE_FULFILLMENT_DATA (async).  Pase 2 cont]] - rationale - trackings.py
- [[_archive_and_cleanup()]] - code - trackings.py
- [[_cleanup_temp()]] - code - trackings.py
- [[_prepare_upload_file()]] - code - trackings.py
- [[_reports_folder()]] - code - library/file_explorer.py
- [[detect_separator()]] - code - library/file_explorer.py
- [[file_explorer.py]] - code - library/file_explorer.py
- [[gunzip_to_text()]] - code - library/helper_functions.py
- [[load_trackings()]] - code - library/file_explorer.py
- [[parse_amazon_report()]] - code - library/file_explorer.py
- [[read_remote_file()]] - code - library/file_explorer.py
- [[save_stock_result()]] - code - library/file_explorer.py
- [[save_tracking_result()]] - code - library/file_explorer.py
- [[save_vat_report()]] - code - library/file_explorer.py
- [[trackings.py]] - code - trackings.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/File_I/O
SORT file.name ASC
```

## Connections to other communities
- 12 edges to [[_COMMUNITY_Stock Module]]
- 9 edges to [[_COMMUNITY_Mailer]]
- 4 edges to [[_COMMUNITY_Runner & VAT]]
- 4 edges to [[_COMMUNITY_Marketplace Catalog]]
- 3 edges to [[_COMMUNITY_Common Config]]
- 2 edges to [[_COMMUNITY_Async Transport & Retry]]
- 2 edges to [[_COMMUNITY_SP-API Exceptions]]
- 2 edges to [[_COMMUNITY_FTP Config]]
- 2 edges to [[_COMMUNITY_Trackings Match Tests]]
- 1 edge to [[_COMMUNITY_Acronyms Config]]

## Top bridge nodes
- [[trackings.py]] - degree 29, connects to 10 communities
- [[file_explorer.py]] - degree 17, connects to 4 communities
- [[save_vat_report()]] - degree 7, connects to 3 communities
- [[gunzip_to_text()]] - degree 5, connects to 3 communities
- [[save_stock_result()]] - degree 4, connects to 2 communities