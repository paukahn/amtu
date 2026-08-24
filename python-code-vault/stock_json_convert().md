---
source_file: "library/stock_feed.py"
type: "code"
community: "Marketplace Catalog"
location: "L113"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Marketplace_Catalog
---

# stock_json_convert()

## Connections
- [[.test_builds_feed_with_stock_and_price()]] - `calls` [EXTRACTED]
- [[.test_invalid_handling_time_drops_stock_patch()]] - `calls` [EXTRACTED]
- [[.test_invalid_min_price_drops_price_patch()]] - `calls` [EXTRACTED]
- [[.test_price_above_max_omits_product()]] - `calls` [EXTRACTED]
- [[.test_price_below_min_omits_product()]] - `calls` [EXTRACTED]
- [[.test_price_equal_to_bound_is_allowed()]] - `calls` [EXTRACTED]
- [[.test_price_out_of_range_omits_even_with_stock()]] - `calls` [EXTRACTED]
- [[.test_price_within_range_publishes_with_bounds()]] - `calls` [EXTRACTED]
- [[.test_row_without_sku_is_skipped()]] - `calls` [EXTRACTED]
- [[.test_stock_only_without_price_publishes()]] - `calls` [EXTRACTED]
- [[_fulfillment_patch()]] - `calls` [EXTRACTED]
- [[_price_patch()]] - `calls` [EXTRACTED]
- [[error()]] - `calls` [EXTRACTED]
- [[locale_of_country()]] - `calls` [EXTRACTED]
- [[stock.py_1]] - `imports` [EXTRACTED]
- [[stock_feed.py]] - `contains` [EXTRACTED]
- [[test_transforms.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Marketplace_Catalog