---
source_file: "REFACTORING.md"
type: "code"
community: "SP-API Exceptions"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/SP-API_Exceptions
---

# AmazonClient.run_report() report orchestrator

## Connections
- [[AmazonClient]] - `implements` [EXTRACTED]
- [[F14 VAT RDT via download_report_content, decompress by compressionAlgorithm]] - `rationale_for` [INFERRED]
- [[F18 run_report raises on CANCELLEDFATAL terminal failure]] - `rationale_for` [EXTRACTED]
- [[F3 orders fallback only on HTTP 400 (not any error)]] - `rationale_for` [INFERRED]

#graphify/code #graphify/EXTRACTED #community/SP-API_Exceptions