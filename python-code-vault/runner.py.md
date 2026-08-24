---
source_file: "library/runner.py"
type: "code"
community: "Runner & VAT"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Runner__VAT
---

# runner.py

## Connections
- [[AccountClients]] - `imports` [EXTRACTED]
- [[AccountsConfig]] - `imports` [EXTRACTED]
- [[CommonConfig]] - `imports` [EXTRACTED]
- [[ConfigError]] - `imports` [EXTRACTED]
- [[F12 invalid config raises ConfigError instead of sys.exit(1)]] - `rationale_for` [INFERRED]
- [[F15 debug mode restored (runner derives debug - AccountClients - AsyncTransport)]] - `rationale_for` [EXTRACTED]
- [[F16 account isolation restored (except Exception + return_exceptions)]] - `rationale_for` [EXTRACTED]
- [[F19 to_thread config decrypt; force_refresh re-check under lock; _poll max(1,attempts); delete_token no secret leak]] - `rationale_for` [INFERRED]
- [[F8 account regions (EUNA) processed in parallel in orders]] - `rationale_for` [INFERRED]
- [[PollingConfig.py]] - `imports_from` [EXTRACTED]
- [[RunContext]] - `contains` [EXTRACTED]
- [[Runner compartido para los módulos (orders  stock  trackings  vat).  Orquesta]] - `rationale_for` [EXTRACTED]
- [[error()]] - `imports` [EXTRACTED]
- [[factory.py]] - `imports_from` [EXTRACTED]
- [[load_master_keys()]] - `imports` [EXTRACTED]
- [[orders.py]] - `imports_from` [EXTRACTED]
- [[run_module()]] - `contains` [EXTRACTED]
- [[run_module_sync()]] - `contains` [EXTRACTED]
- [[set_log_context()]] - `imports` [EXTRACTED]
- [[stock.py_1]] - `imports_from` [EXTRACTED]
- [[test_runner_isolation.py]] - `imports_from` [EXTRACTED]
- [[trackings.py]] - `imports_from` [EXTRACTED]
- [[vat_report.py]] - `imports_from` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Runner__VAT