---
type: community
cohesion: 0.07
members: 53
---

# Marketplace Catalog

**Cohesion:** 0.07 - loosely connected
**Members:** 53 nodes

## Members
- [[.__init__()_15]] - code - library/spapi_client.py
- [[.test_blocks_when_too_many_dropped()]] - code - tests/test_transforms.py
- [[.test_boundary_ratio_is_allowed()]] - code - tests/test_transforms.py
- [[.test_builds_feed_with_stock_and_price()]] - code - tests/test_transforms.py
- [[.test_endpoints_match_region_grouping()]] - code - tests/test_marketplaces.py
- [[.test_every_entry_is_complete()]] - code - tests/test_marketplaces.py
- [[.test_inputs_are_normalized()]] - code - tests/test_marketplaces.py
- [[.test_invalid_handling_time_drops_stock_patch()]] - code - tests/test_transforms.py
- [[.test_invalid_min_price_drops_price_patch()]] - code - tests/test_transforms.py
- [[.test_known_values_preserved()]] - code - tests/test_marketplaces.py
- [[.test_passes_when_ratio_above_min()]] - code - tests/test_transforms.py
- [[.test_previously_missing_countries_now_resolve()]] - code - tests/test_marketplaces.py
- [[.test_price_above_max_omits_product()]] - code - tests/test_transforms.py
- [[.test_price_below_min_omits_product()]] - code - tests/test_transforms.py
- [[.test_price_equal_to_bound_is_allowed()]] - code - tests/test_transforms.py
- [[.test_price_out_of_range_omits_even_with_stock()]] - code - tests/test_transforms.py
- [[.test_price_within_range_publishes_with_bounds()]] - code - tests/test_transforms.py
- [[.test_row_without_sku_is_skipped()]] - code - tests/test_transforms.py
- [[.test_small_feeds_skip_guard()]] - code - tests/test_transforms.py
- [[.test_stock_only_without_price_publishes()]] - code - tests/test_transforms.py
- [[Construcción del feed JSON_LISTINGS_FEED de stockprecios.  Descompone el god-me]] - rationale - library/stock_feed.py
- [[Endpoint SP-API + región AWS + tiendas de un mercado ('eu'  'na').]] - rationale - library/marketplaces.py
- [[F20 send_tracking_feed checks s3_put status, raises on failure (avoids empty feed + data loss)]] - rationale - REFACTORING.md
- [[F21 stock removed spurious content_encoding=gzip (SP-API Feeds contract)]] - rationale - REFACTORING.md
- [[F22 trackings TSV cleanup on S3 fail; stock _verify_feed honors compressionAlgorithm; PII_REQUIRED typo fix]] - rationale - REFACTORING.md
- [[F2 extra marketplaces (be,nl,za,eg,tr,sa,ae,in,br) resolve regioncurrencylocale]] - rationale - REFACTORING.md
- [[F9 stock regionmarket check before download; S3 != 200 skips feed]] - rationale - REFACTORING.md
- [[Golden tests de la transformación del feed de stock (sin red ni API).  Fijan la]] - rationale - tests/test_transforms.py
- [[Marketplace]] - code - library/marketplaces.py
- [[NamedTuple]] - code
- [[Patch de precio. Devuelve (patch  None, fuera_de_rango).]] - rationale - library/stock_feed.py
- [[Patch de stock (quantity + handling time), o None si no aplica.]] - rationale - library/stock_feed.py
- [[TestMarketplaces]] - code - tests/test_marketplaces.py
- [[TestStockJsonConvert]] - code - tests/test_transforms.py
- [[TestStockSanityCheck]] - code - tests/test_transforms.py
- [[Tests del catálogo único de marketplaces (librarymarketplaces.py).  Verifican l]] - rationale - tests/test_marketplaces.py
- [[_fulfillment_patch()]] - code - library/stock_feed.py
- [[_price_patch()]] - code - library/stock_feed.py
- [[currency()]] - code - library/marketplaces.py
- [[get_market_endpoints()]] - code - library/marketplaces.py
- [[get_marketplace()]] - code - library/marketplaces.py
- [[get_store_identifier()]] - code - library/marketplaces.py
- [[locale_of_country()]] - code - library/marketplaces.py
- [[marketplaces.py]] - code - library/marketplaces.py
- [[process_account()_1]] - code - trackings.py
- [[region_of_country()]] - code - library/marketplaces.py
- [[stock_feed.py]] - code - library/stock_feed.py
- [[stock_json_convert()]] - code - library/stock_feed.py
- [[stock_sanity_check()]] - code - library/stock_feed.py
- [[test_marketplaces.py]] - code - tests/test_marketplaces.py
- [[test_transforms.py]] - code - tests/test_transforms.py
- [[¿Es seguro publicar este feed al catálogo vivo      Protege contra un fichero r]] - rationale - library/stock_feed.py
- [[Único punto de verdad de los metadatos de marketplaces de Amazon.  Sustituye a l]] - rationale - library/marketplaces.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Marketplace_Catalog
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_Stock Module]]
- 5 edges to [[_COMMUNITY_Orders Module]]
- 4 edges to [[_COMMUNITY_Runner & VAT]]
- 4 edges to [[_COMMUNITY_Mailer]]
- 4 edges to [[_COMMUNITY_File IO]]
- 3 edges to [[_COMMUNITY_SP-API Exceptions]]
- 1 edge to [[_COMMUNITY_Acronyms Config]]
- 1 edge to [[_COMMUNITY_Common Config]]
- 1 edge to [[_COMMUNITY_Trackings Match Tests]]

## Top bridge nodes
- [[process_account()_1]] - degree 9, connects to 7 communities
- [[marketplaces.py]] - degree 16, connects to 5 communities
- [[get_store_identifier()]] - degree 13, connects to 4 communities
- [[region_of_country()]] - degree 13, connects to 3 communities
- [[stock_json_convert()]] - degree 17, connects to 2 communities