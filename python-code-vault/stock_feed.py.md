---
source_file: "library/stock_feed.py"
type: "code"
community: "Marketplace Catalog"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Marketplace_Catalog
---

# stock_feed.py

## Connections
- [[Construcción del feed JSON_LISTINGS_FEED de stockprecios.  Descompone el god-me]] - `rationale_for` [EXTRACTED]
- [[F21 stock removed spurious content_encoding=gzip (SP-API Feeds contract)]] - `rationale_for` [EXTRACTED]
- [[F22 trackings TSV cleanup on S3 fail; stock _verify_feed honors compressionAlgorithm; PII_REQUIRED typo fix]] - `rationale_for` [INFERRED]
- [[F24b stock sanity-guard (min valid SKU ratio, mail alert, do not publish)]] - `rationale_for` [EXTRACTED]
- [[F9 stock regionmarket check before download; S3 != 200 skips feed]] - `rationale_for` [INFERRED]
- [[_fulfillment_patch()]] - `contains` [EXTRACTED]
- [[_price_patch()]] - `contains` [EXTRACTED]
- [[currency()]] - `imports` [EXTRACTED]
- [[error()]] - `imports` [EXTRACTED]
- [[locale_of_country()]] - `imports` [EXTRACTED]
- [[marketplaces.py]] - `imports_from` [EXTRACTED]
- [[stock.py_1]] - `imports_from` [EXTRACTED]
- [[stock_json_convert()]] - `contains` [EXTRACTED]
- [[stock_sanity_check()]] - `contains` [EXTRACTED]
- [[test_transforms.py]] - `imports_from` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Marketplace_Catalog