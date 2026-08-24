---
source_file: "library/spapi_client.py"
type: "code"
community: "SP-API Exceptions"
location: "L61"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/SP-API_Exceptions
---

# AmazonClient

## Connections
- [[.__init__()_15]] - `method` [EXTRACTED]
- [[._call()]] - `method` [EXTRACTED]
- [[._poll()]] - `method` [EXTRACTED]
- [[.client()]] - `references` [EXTRACTED]
- [[.create_feed_document()]] - `method` [EXTRACTED]
- [[.create_report()]] - `method` [EXTRACTED]
- [[.download_bytes()]] - `method` [EXTRACTED]
- [[.download_report_content()]] - `method` [EXTRACTED]
- [[.download_text()]] - `method` [EXTRACTED]
- [[.get_feed_result_document()]] - `method` [EXTRACTED]
- [[.get_feed_status()]] - `method` [EXTRACTED]
- [[.get_report_document()]] - `method` [EXTRACTED]
- [[.get_report_status()]] - `method` [EXTRACTED]
- [[.get_restricted_data_token()]] - `method` [EXTRACTED]
- [[.run_report()]] - `method` [EXTRACTED]
- [[.s3_put()]] - `method` [EXTRACTED]
- [[.send_feed()]] - `method` [EXTRACTED]
- [[.send_tracking_feed()]] - `method` [EXTRACTED]
- [[AccountClients]] - `uses` [INFERRED]
- [[AmazonAPIError]] - `uses` [INFERRED]
- [[AmazonAuthError]] - `uses` [INFERRED]
- [[AmazonClient.run_report() report orchestrator]] - `implements` [EXTRACTED]
- [[AmazonFeedNotReadyError]] - `uses` [INFERRED]
- [[AmazonReportNotReadyError]] - `uses` [INFERRED]
- [[AsyncTokenProvider]] - `calls` [INFERRED]
- [[AsyncTransport]] - `calls` [EXTRACTED]
- [[B2 factorjitter parsed but unused]] - `rationale_for` [EXTRACTED]
- [[B5 401 did not refresh token (only 429 handled)]] - `rationale_for` [EXTRACTED]
- [[Call chain module - AmazonClient - AsyncTransport - httpx.AsyncClient]] - `references` [EXTRACTED]
- [[CreateFeedDocumentResponse]] - `uses` [INFERRED]
- [[CreateFeedResponse]] - `uses` [INFERRED]
- [[CreateReportResponse]] - `uses` [INFERRED]
- [[FakePolling]] - `uses` [INFERRED]
- [[FakeTokens]] - `uses` [INFERRED]
- [[FeedDocumentResponse]] - `uses` [INFERRED]
- [[FeedStatusResponse]] - `uses` [INFERRED]
- [[ReportDocumentResponse]] - `uses` [INFERRED]
- [[ReportRun]] - `uses` [INFERRED]
- [[ReportStatusResponse]] - `uses` [INFERRED]
- [[RestrictedDataTokenResponse]] - `uses` [INFERRED]
- [[TestClient]] - `uses` [INFERRED]
- [[build_client()]] - `calls` [EXTRACTED]
- [[factory.py]] - `imports` [EXTRACTED]
- [[pydantic==2.12.4]] - `references` [INFERRED]
- [[spapi_client.py]] - `contains` [EXTRACTED]
- [[test_client.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/SP-API_Exceptions