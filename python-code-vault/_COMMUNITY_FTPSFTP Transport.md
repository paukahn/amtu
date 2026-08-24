---
type: community
cohesion: 0.28
members: 9
---

# FTP/SFTP Transport

**Cohesion:** 0.28 - loosely connected
**Members:** 9 nodes

## Members
- [[Envía `local_path` según `cfg` (hostusernamepasswordfolder_inportftp_mode).]] - rationale - library/ftp_transport.py
- [[Envío de ficheros por FTPSFTP (mecánica de red, sin configuración).  Separado d]] - rationale - library/ftp_transport.py
- [[F1 FTP order upload gate revived (FTPConfig is_active)]] - rationale - REFACTORING.md
- [[FTPConfig (config + FTP policy)]] - code - REFACTORING.md
- [[_send_ftp()]] - code - library/ftp_transport.py
- [[_send_sftp()]] - code - library/ftp_transport.py
- [[ftp_transport.py]] - code - library/ftp_transport.py
- [[paramiko==4.0.0]] - concept - requirements.txt
- [[send_file()]] - code - library/ftp_transport.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/FTP/SFTP_Transport
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Config Save]]

## Top bridge nodes
- [[send_file()]] - degree 5, connects to 1 community