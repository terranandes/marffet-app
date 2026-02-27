# Code Review - 2026-02-27 Sync 1903

**Date:** 2026-02-27 19:03 HKT
**Reviewer:** [CV]
**Author:** [CODE]
**Topic:** Calculation Service Accuracy (Trend & My Race Timeline Fixes)
**Status:** Approved

## 1. Summary of Changes
Modifications were made purely to `app/services/calculation_service.py` targeting the data aggregation layers for the frontend visualization charts.

## 2. Review Details

### 2.1 Trend Chart Value Stitching (`get_portfolio_history`)
- **[APPROVED]** The logic successfully instantiates `live_prices = market_data_service.fetch_live_prices(stock_ids)` *outside* of the `while current_iter_date <= end_date` loop, preventing redundant expensive external YFinance round-trips algorithmically.
- **[APPROVED]** Inside the price evaluator, the `if month_key == current_real_month and sid in live_prices:` switch cleanly skips the standard DuckDB `nearest` indexer, mathematically substituting the Live price instead. This effectively bridges the historical monthly timeline to the exact live Dashboard totals.

### 2.2 My Race Name Collision Patch (`get_portfolio_race_data`)
- **[APPROVED]** Re-structured the `target_map` list comprehension to explicitly map the underlying `stock_id` inside the dictionary values: `target_map = {t['id']: {'stock_id': t['stock_id'], ... }}`.
- **[APPROVED]** Fixed the leaky downstream iteration: 
  ```python
  for t in target_map.values():
      if t.get('stock_id') == sid and t.get('name') and t.get('name') != sid: 
           ...
  ```
  This guarantees strict referential matching between the aggregated numeric loop (`sid`) and the mapped display metadata.

## 3. Security & Performance
- **Performance:** Injecting `market_data_service.fetch_live_prices` adds negligible overhead since it leverages the existing `MarketCache` singleton and batch queries.
- **Security:** No new endpoints were exposed. Existing dependency injections and API schemas remain intact. 

## 4. Conclusion
The changes are isolated and robust. The UI layer will automatically inherit the sanitized JSON payloads. Deployed to master safely.
