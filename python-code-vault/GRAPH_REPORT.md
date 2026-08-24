# Graph Report - .  (2026-07-02)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 636 nodes · 1406 edges · 44 communities (30 shown, 14 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 111 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_SP-API Exceptions|SP-API Exceptions]]
- [[_COMMUNITY_Marketplace Catalog|Marketplace Catalog]]
- [[_COMMUNITY_Client Factory|Client Factory]]
- [[_COMMUNITY_Async Transport & Retry|Async Transport & Retry]]
- [[_COMMUNITY_FTP Config|FTP Config]]
- [[_COMMUNITY_LWA Token Provider|LWA Token Provider]]
- [[_COMMUNITY_Applications Config|Applications Config]]
- [[_COMMUNITY_Master-Key Crypto & CLI|Master-Key Crypto & CLI]]
- [[_COMMUNITY_File IO|File I/O]]
- [[_COMMUNITY_Config Save|Config Save]]
- [[_COMMUNITY_Orders Module|Orders Module]]
- [[_COMMUNITY_Logging (Logger)|Logging (Logger)]]
- [[_COMMUNITY_Runner & VAT|Runner & VAT]]
- [[_COMMUNITY_DataTransformer (SAP)|DataTransformer (SAP)]]
- [[_COMMUNITY_Common Config|Common Config]]
- [[_COMMUNITY_Stock Module|Stock Module]]
- [[_COMMUNITY_Stock Config|Stock Config]]
- [[_COMMUNITY_Config Parser (base)|Config Parser (base)]]
- [[_COMMUNITY_Polling Config|Polling Config]]
- [[_COMMUNITY_Mailer|Mailer]]
- [[_COMMUNITY_Async Migration (B1-B7)|Async Migration (B1-B7)]]
- [[_COMMUNITY_Accounts Config|Accounts Config]]
- [[_COMMUNITY_Acronyms Config|Acronyms Config]]
- [[_COMMUNITY_Mail Config|Mail Config]]
- [[_COMMUNITY_Trackings Match Tests|Trackings Match Tests]]
- [[_COMMUNITY_FTPSFTP Transport|FTP/SFTP Transport]]
- [[_COMMUNITY_Logging Helpers|Logging Helpers]]
- [[_COMMUNITY_Config Read|Config Read]]
- [[_COMMUNITY_save_sections Tests|save_sections Tests]]
- [[_COMMUNITY_DataTransformer Fixes|DataTransformer Fixes]]
- [[_COMMUNITY_Runner Isolation Test|Runner Isolation Test]]
- [[_COMMUNITY_Case-Sensitivity Fixes|Case-Sensitivity Fixes]]
- [[_COMMUNITY_Dependencies|Dependencies]]
- [[_COMMUNITY_graphify output|graphify output]]
- [[_COMMUNITY_amtubb project|amtubb project]]
- [[_COMMUNITY_Fix CLI --tokens (F13)|Fix CLI --tokens (F13)]]
- [[_COMMUNITY_Fix raw archive (F23c)|Fix raw archive (F23c)]]
- [[_COMMUNITY_Fix trackings delete (F23d)|Fix trackings delete (F23d)]]
- [[_COMMUNITY_Orders date window (F27)|Orders date window (F27)]]
- [[_COMMUNITY_Fix VAT dir (F7)|Fix VAT dir (F7)]]

## God Nodes (most connected - your core abstractions)
1. `AmazonClient` - 46 edges
2. `error()` - 35 edges
3. `info()` - 35 edges
4. `AsyncTransport` - 34 edges
5. `ConfigError` - 32 edges
6. `CommonConfig` - 26 edges
7. `AmazonAPIError` - 24 edges
8. `ApplicationsConfig` - 23 edges
9. `parse_sections()` - 22 edges
10. `config_path()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `F23a: access-token cache encrypted at rest (AES+HMAC via data_protector)` --rationale_for--> `AsyncTokenProvider`  [INFERRED]
  REFACTORING.md → library/auth_provider.py
- `F12: invalid config raises ConfigError instead of sys.exit(1)` --rationale_for--> `ConfigError`  [EXTRACTED]
  REFACTORING.md → classes/config/base.py
- `F17: quota-in-body AmazonThrottleError carries status/body; atomic token cache (os.replace)` --rationale_for--> `AsyncTokenProvider`  [INFERRED]
  REFACTORING.md → library/auth_provider.py
- `AmazonClient` --references--> `pydantic==2.12.4`  [INFERRED]
  library/spapi_client.py → requirements.txt
- `B5: 401 did not refresh token (only 429 handled)` --rationale_for--> `AmazonClient`  [EXTRACTED]
  MIGRATION.md → library/spapi_client.py

## Import Cycles
- None detected.

## Communities (44 total, 14 thin omitted)

### Community 0 - "SP-API Exceptions"
Cohesion: 0.08
Nodes (34): BaseModel, Exception, AmazonAPIError, AmazonFeedNotReadyError, AmazonReportNotReadyError, Errores generales de la API.      `status_code`/`body` permiten a los llamadores, Feed processing (IN_QUEUE / IN_PROGRESS), Report processing (IN_QUEUE / IN_PROGRESS) (+26 more)

### Community 1 - "Marketplace Catalog"
Cohesion: 0.07
Nodes (29): currency(), get_market_endpoints(), get_marketplace(), get_store_identifier(), locale_of_country(), Marketplace, Único punto de verdad de los metadatos de marketplaces de Amazon.  Sustituye a l, Endpoint SP-API + región AWS + tiendas de un mercado ('eu' | 'na'). (+21 more)

### Community 2 - "Client Factory"
Cohesion: 0.06
Nodes (18): AccountClients, Factory: ensambla los recursos async de una cuenta y produce AmazonClient.  Reem, AsyncTokenBucket, Async rate limiter for the Amazon SP-API (token-bucket per region:endpoint).  Re, Actualiza el rate desde la cabecera de respuesta de Amazon.          Es síncrono, B1: rate-limiter no-op (read _rates not _last_call), build_client(), FakePolling (+10 more)

### Community 3 - "Async Transport & Retry"
Cohesion: 0.10
Nodes (22): AmazonAuthError, AmazonServerError, AmazonThrottleError, Error 429 / Quota Exceeded, Error 5xx de la SP-API (transitorio: se reintenta en el transporte), Error 401 (Unauthorized), AsyncTransport, AsyncClient (+14 more)

### Community 4 - "FTP Config"
Cohesion: 0.12
Nodes (31): main(), FTPConfig, ¿Hay transporte configurado Y activo para la cuenta?, Cuentas de transporte FTP/SFTP (ftp_accounts.amzaccs, cifrado).      Pase 2: la, create_or_edit_application(), delete_app(), edit_app_section(), list_apps() (+23 more)

### Community 5 - "LWA Token Provider"
Cohesion: 0.08
Nodes (21): BaseException, AsyncTokenProvider, _is_transient_lwa_error(), Proveedor de tokens async para LWA (Login With Amazon).  Mismo papel que en el p, Devuelve (token, expires_at).      Con key/hmac_key el fichero se descifra (AES+, _read_cache(), _still_valid(), _write_cache() (+13 more)

### Community 6 - "Applications Config"
Cohesion: 0.09
Nodes (11): ApplicationsConfig, Credenciales LWA de las aplicaciones (applications.amzapps, cifrado)., AsyncClient, _local_output_name(), _orders_date_range(), Nombre del fichero local de pedidos: acrónimo y 'amz' en MINÚSCULAS.      El con, Ventana de pedidos del original: desde las 00:00 de hace 7 días hasta AHORA., Nombre del fichero local de pedidos: acrónimo y 'amz' en minúsculas.  El consumi (+3 more)

### Community 7 - "Master-Key Crypto & CLI"
Cohesion: 0.13
Nodes (15): _derive_v1(), _derive_v2(), encrypt_keys(), load_keys(), _load_v1(), _load_v2(), pad(), Cifrado de la llave maestra en secret_keys.bin (ruta CLI con contraseña).  Forma (+7 more)

### Community 8 - "File I/O"
Cohesion: 0.13
Nodes (19): detect_separator(), load_trackings(), parse_amazon_report(), DataFrame, E/S de ficheros locales y remotos de los módulos.  Cambios del pase 2: - Sin sid, Guarda los datos del reporte fiscal (ya procesados) en un archivo TSV     bajo <, Detecta automáticamente si el contenido está separado por tabulaciones o comas u, Lee archivo remoto (CSV o TSV) detectando automáticamente el separador.     BLOQ (+11 more)

### Community 9 - "Config Save"
Cohesion: 0.20
Nodes (9): Serializa y guarda el archivo cifrado con el estado actual de las apps., config_path(), parse_flat(), Base compartida del paquete de configuración (pase 2 del refactor).  Sustituye l, Parsea `clave = valor` por línea, sin secciones. '#'/';' a línea completa., Serializa {sección: {clave: valor}} al formato `[sección]` / `k = v`.      Manti, save_sections(), Tests del parser base de configuración (classes/config/base.py). (+1 more)

### Community 10 - "Orders Module"
Cohesion: 0.16
Nodes (16): archive_final(), archive_raw(), _clean_tsv_lines(), extract_xml_info(), process_orders_account(), _process_region(), _process_region_guarded(), Módulo de pedidos: reportes de órdenes (TSV + XML) -> SAP -> FTP (async).  Pase (+8 more)

### Community 11 - "Logging (Logger)"
Cohesion: 0.18
Nodes (5): ColorFormatter, Logger, Configurar el logger con separación entre operaciones exitosas, errores y depura, Devuelve el logger configurado., Obtiene un logger específico para una tienda y nivel (success/error).         s

### Community 12 - "Runner & VAT"
Cohesion: 0.15
Nodes (15): set_log_context(), Runner compartido para los módulos (orders / stock / trackings / vat).  Orquesta, run_module(), RunContext, F12: invalid config raises ConfigError instead of sys.exit(1), F15: debug mode restored (runner derives debug -> AccountClients -> AsyncTransport), F16: account isolation restored (except Exception + return_exceptions), F8: account regions (EU/NA) processed in parallel in orders (+7 more)

### Community 13 - "DataTransformer (SAP)"
Cohesion: 0.20
Nodes (5): DataTransformer, Expande una plantilla de CONFIG con context_vars + fila.          Tolera plant, _make_transformer(), DataTransformer._apply_logic: format_map SOLO sobre plantillas de config.  Antes, TestApplyLogicFormatMap

### Community 14 - "Common Config"
Cohesion: 0.16
Nodes (4): CommonConfig, Fracción mínima de filas con SKU válido para publicar el feed (sanity-guard)., Maneja configuración global común desde common.ini.     reports_folder es obliga, Nº de filas a partir del cual aplicar el sanity-guard del stock.

### Community 15 - "Stock Module"
Cohesion: 0.28
Nodes (12): archive_sent_stock_tsv(), info(), Imprime mensajes informativos (success).      Args:         message (str | bytes, run_module_sync(), main(), main(), process_account(), Módulo de stock/precios: feed JSON_LISTINGS_FEED (async).  Pase 2: - Contrato nu (+4 more)

### Community 16 - "Stock Config"
Cohesion: 0.26
Nodes (4): ConfigError, Configuración ausente, ilegible o inválida., Carga la configuración de stocks desde stock.ini.     Claves permitidas: las que, StockConfig

### Community 17 - "Config Parser (base)"
Cohesion: 0.29
Nodes (3): parse_sections(), Parsea texto tipo INI a {sección: [(clave, valor), ...]}.      - Los nombres de, TestParseSections

### Community 19 - "Mailer"
Cohesion: 0.25
Nodes (10): load_mails(), error(), Imprime mensajes de error o advertencia.      Args:         message (str | bytes, notify_error_mail(), Notificaciones por correo (SMTP). Separado de helper_functions en el pase 2.  El, Envía un correo usando SMTP seguro.     :param recipient: Destinatario     :para, Envía `body` a todos los correos de config/emails.txt.      Carga MailConfig UNA, send_mail() (+2 more)

### Community 20 - "Async Migration (B1-B7)"
Cohesion: 0.18
Nodes (11): Async refactor of SP-API integration, B3: .env.secret hex vs 64 raw bytes mismatch, B4: dead enrich_feed_with_product_types removed, Call chain: module -> AmazonClient -> AsyncTransport -> httpx.AsyncClient, Refactor without observable behavior change (pass 1), asyncio.to_thread for blocking ops (pandas/files/SMTP/FTP), data_protector (AES+HMAC encryption helper), F11: brand_analytics module removed (never worked, optional) (+3 more)

### Community 24 - "Trackings Match Tests"
Cohesion: 0.31
Nodes (4): Match de fichero de trackings por acrónimo, sin distinguir mayúsculas.  Regresió, TestBelongsToAcronym, _belongs_to_acronym(), ¿El fichero pertenece a esta cuenta? Prefijo `acronimo_` SIN distinguir     mayú

### Community 25 - "FTP/SFTP Transport"
Cohesion: 0.28
Nodes (8): Envío de ficheros por FTP/SFTP (mecánica de red, sin configuración).  Separado d, Envía `local_path` según `cfg` (host/username/password/folder_in/port/ftp_mode)., send_file(), _send_ftp(), _send_sftp(), F1: FTP order upload gate revived (FTPConfig is_active), FTPConfig (config + FTP policy), paramiko==4.0.0

### Community 26 - "Logging Helpers"
Cohesion: 0.32
Nodes (4): debug(), _ensure(), Funciones de logging del proyecto (info / error / debug + contexto).  Pase 2: la, Imprime mensajes de depuración (solo en modo debug).      Args:         message

### Community 27 - "Config Read"
Cohesion: 0.33
Nodes (3): Lee el fichero como texto; si hay llaves, lo descifra antes., read_config_text(), TestReadConfigText

### Community 29 - "DataTransformer Fixes"
Cohesion: 0.50
Nodes (4): B6: detect_separator got route not content, DataTransformer, F23e: DataTransformer format_map only on config templates, never Amazon data, pandas==2.2.3

### Community 31 - "Case-Sensitivity Fixes"
Cohesion: 0.67
Nodes (3): Account acronym: cosmic -> COS, F25: trackings acronym file match case-insensitive (_belongs_to_acronym), F26: orders local file uses lowercase acronym+amz ({id}_cos_amz.txt)

## Knowledge Gaps
- **8 isolated node(s):** `amtubb`, `httpx==0.28.1`, `tenacity==9.1.2`, `pydantic==2.12.4`, `pandas==2.2.3` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AmazonClient` connect `SP-API Exceptions` to `Marketplace Catalog`, `Client Factory`, `Async Transport & Retry`, `LWA Token Provider`, `Async Migration (B1-B7)`, `Logging Helpers`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Why does `error()` connect `Mailer` to `Marketplace Catalog`, `FTP Config`, `LWA Token Provider`, `File I/O`, `Config Save`, `Orders Module`, `Runner & VAT`, `Stock Module`, `Logging Helpers`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `ConfigError` connect `Stock Config` to `SP-API Exceptions`, `Applications Config`, `Master-Key Crypto & CLI`, `Config Save`, `Runner & VAT`, `Common Config`, `Config Parser (base)`, `Polling Config`, `Accounts Config`, `Acronyms Config`, `Mail Config`, `Config Read`, `save_sections Tests`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `AmazonClient` (e.g. with `AccountClients` and `AsyncTokenProvider`) actually correct?**
  _`AmazonClient` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AsyncTransport` (e.g. with `AccountClients` and `AmazonAuthError`) actually correct?**
  _`AsyncTransport` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `ConfigError` (e.g. with `AccountsConfig` and `ApplicationsConfig`) actually correct?**
  _`ConfigError` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Cuentas de vendedor (accounts.ini).      Ya no es singleton: cada construcción r`, `Acrónimos por cuenta (acronyms.txt). Fichero ausente => sin acrónimos.      Sin`, `Credenciales LWA de las aplicaciones (applications.amzapps, cifrado).` to the rest of the system?**
  _132 weakly-connected nodes found - possible documentation gaps or missing edges._