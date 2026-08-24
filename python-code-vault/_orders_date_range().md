---
source_file: "orders.py"
type: "code"
community: "Applications Config"
location: "L126"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Applications_Config
---

# _orders_date_range()

## Connections
- [[.test_start_is_midnight()]] - `calls` [EXTRACTED]
- [[.test_window_is_7_days_ending_now()]] - `calls` [EXTRACTED]
- [[Ventana de pedidos del original desde las 0000 de hace 7 días hasta AHORA.]] - `rationale_for` [EXTRACTED]
- [[orders.py]] - `contains` [EXTRACTED]
- [[process_orders_account()]] - `calls` [EXTRACTED]
- [[test_orders_naming.py]] - `imports` [EXTRACTED]
- [[timedelta]] - `calls` [INFERRED]

#graphify/code #graphify/EXTRACTED #community/Applications_Config