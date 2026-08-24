---
source_file: "library/exceptions.py"
type: "code"
community: "SP-API Exceptions"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/SP-API_Exceptions
---

# AmazonAPIError

## Connections
- [[.__init__()_12]] - `method` [EXTRACTED]
- [[.create_report()]] - `calls` [EXTRACTED]
- [[.run_report()]] - `calls` [EXTRACTED]
- [[.send_tracking_feed()]] - `calls` [EXTRACTED]
- [[.test_400_falls_back_to_general_type()]] - `calls` [EXTRACTED]
- [[.test_other_errors_propagate_without_fallback()]] - `calls` [EXTRACTED]
- [[AmazonAuthError]] - `inherits` [EXTRACTED]
- [[AmazonClient]] - `uses` [INFERRED]
- [[AmazonFeedNotReadyError]] - `inherits` [EXTRACTED]
- [[AmazonReportNotReadyError]] - `inherits` [EXTRACTED]
- [[AmazonServerError]] - `inherits` [EXTRACTED]
- [[AmazonThrottleError]] - `inherits` [EXTRACTED]
- [[Errores generales de la API.      `status_code``body` permiten a los llamadores]] - `rationale_for` [EXTRACTED]
- [[Exception]] - `inherits` [EXTRACTED]
- [[FakeClient]] - `uses` [INFERRED]
- [[FakePolling]] - `uses` [INFERRED]
- [[FakeTokens]] - `uses` [INFERRED]
- [[TestClient]] - `uses` [INFERRED]
- [[TestOrdersFallback]] - `uses` [INFERRED]
- [[exceptions.py]] - `contains` [EXTRACTED]
- [[orders.py]] - `imports` [EXTRACTED]
- [[spapi_client.py]] - `imports` [EXTRACTED]
- [[test_client.py]] - `imports` [EXTRACTED]
- [[test_orders_fallback.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/SP-API_Exceptions