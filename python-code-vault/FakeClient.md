---
source_file: "tests/test_orders_fallback.py"
type: "code"
community: "SP-API Exceptions"
location: "L18"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/SP-API_Exceptions
---

# FakeClient

## Connections
- [[.__init__()_19]] - `method` [EXTRACTED]
- [[.run_report()_1]] - `method` [EXTRACTED]
- [[.test_400_falls_back_to_general_type()]] - `calls` [EXTRACTED]
- [[.test_na_uses_shipping_type()]] - `calls` [EXTRACTED]
- [[.test_other_errors_propagate_without_fallback()]] - `calls` [EXTRACTED]
- [[.test_poll_exhaustion_degrades_to_none_not_fallback()]] - `calls` [EXTRACTED]
- [[.test_success_does_not_fall_back()]] - `calls` [EXTRACTED]
- [[AmazonAPIError]] - `uses` [INFERRED]
- [[AmazonReportNotReadyError]] - `uses` [INFERRED]
- [[ReportRun]] - `uses` [INFERRED]
- [[test_orders_fallback.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/SP-API_Exceptions