---
source_file: "tests/test_orders_fallback.py"
type: "code"
community: "SP-API Exceptions"
location: "L30"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/SP-API_Exceptions
---

# TestOrdersFallback

## Connections
- [[.test_400_falls_back_to_general_type()]] - `method` [EXTRACTED]
- [[.test_na_uses_shipping_type()]] - `method` [EXTRACTED]
- [[.test_other_errors_propagate_without_fallback()]] - `method` [EXTRACTED]
- [[.test_poll_exhaustion_degrades_to_none_not_fallback()]] - `method` [EXTRACTED]
- [[.test_success_does_not_fall_back()]] - `method` [EXTRACTED]
- [[AmazonAPIError]] - `uses` [INFERRED]
- [[AmazonReportNotReadyError]] - `uses` [INFERRED]
- [[ReportRun]] - `uses` [INFERRED]
- [[test_orders_fallback.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/SP-API_Exceptions