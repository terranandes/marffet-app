# PRD: DuckDB Architecture Migration (Project Martian)

## Overview

Replace the JSON-based `MarketCache` (2.7GB RAM) with a DuckDB columnar database (~50MB RAM) to permanently solve Zeabur OOM crashes. This migration affects all market data consumers (Trend, Race, Mars, CB, Portfolio tabs), the backfill pipeline, admin operations, and cron jobs. User data (`portfolio.db`) is **preserved untouched**.

**Background:** The current architecture loads ~113 JSON files into an in-memory Python dictionary on startup. This requires 2.7GB RAM, far exceeding Zeabur's 512MB container limit. A temporary "Hybrid Cache" (2-year RAM + SQLite fallback) stabilized the server but introduced inaccurate Volatility metrics for historical periods (Monthly data instead of Daily).

**Success Criteria:**
- Zeabur RAM usage < 200MB at steady state
- All tabs return identical data (CAGR, prices) as current system
- Mars Strategy Volatility uses real daily data (not monthly approximation)
- Startup time < 5 seconds (down from 30-60s)
- All crons produce expected output

---

## Task 1: DuckDB Engine & Schema

Install `duckdb` dependency. Create `app/services/market_db.py` with three tables: `daily_prices` (stock_id, date, OHLCV, market), `dividends` (stock_id, year, cash, stock), `stocks` (stock_id, name, market_type, industry). Include `init_schema()` function.

- Add `duckdb` to `pyproject.toml`
- Create `app/services/market_db.py`
- Write unit test: schema creation, table existence
- Verify: `uv run pytest tests/unit/test_market_db.py -v`

## Task 2: JSON → DuckDB Migration Script

Create `scripts/ops/migrate_json_to_duckdb.py`. Read all `data/raw/Market_{Year}_Prices.json`, `TPEx_Market_{Year}_Prices.json`, and `TWSE_Dividends_{Year}.json`. Parse daily OHLCV data and batch INSERT into DuckDB. Report total rows inserted, distinct stocks, and time taken.

- Handle both V1 (yearly summary) and V2 (daily array) JSON schema
- Include row-count validation against source JSON
- Must be idempotent (re-runnable without duplicates via INSERT OR REPLACE)
- Verify: Row count matches expected (~110M rows for 2500 stocks × 250 days × 26 years)

## Task 3: MarketDataProvider (Read Layer)

Create `app/services/market_data_provider.py` as the **single abstraction** for all market data reads. Replaces `MarketCache.get_stock_history_fast()`, `MarketCache.get_strategy_history()`, `MarketCache.get_prices_db()`, and all `race_cache` queries.

Methods:
- `get_daily_history(stock_id, start_date, end_date)` → Full daily OHLCV (Mars Strategy)
- `get_latest_price(stock_id)` → Latest close (Dashboard, CB)
- `get_monthly_closes(stock_ids, start_year)` → Month-end closes (Race, Trend)
- `get_dividends(stock_id, start_year)` → Dividend history (ROI calculation)
- `get_stock_list()` → All known stock IDs
- `warm_latest_cache()` → Load latest price for all stocks into tiny RAM cache (~175KB)

All methods use `duckdb.connect(read_only=True)` for thread-safe concurrent reads.

## Task 4: Rewrite Backfill Writer

Modify `app/services/market_data_service.py`:
- Replace `_save_json_safe()` with `_save_to_duckdb(stock_id, year, daily_data, dividends)`
- Replace `flush_results()` JSON buffer with DuckDB batch INSERT (ACID transactions)
- Remove `_merge_data_dict()` (DuckDB handles INSERT OR REPLACE natively)
- `backfill_all_stocks()` writes directly to DuckDB file

Must maintain: progress_callback, chunk processing, error handling, GC strategy.

## Task 5: Update Calculation Service (Trend + Race + Portfolio)

Modify `app/services/calculation_service.py`:
- `get_portfolio_history()` → Use `MarketDataProvider.get_daily_history()`
- `get_portfolio_race_data()` → Use `MarketDataProvider.get_monthly_closes()`
- `_fetch_prices_from_market_cache()` → Replace with `MarketDataProvider` calls
- `get_target_summary()` → Use `MarketDataProvider.get_latest_price()`
- Remove all `MarketCache` imports

## Task 6: Update Strategy Service (Mars + CB)

Modify `app/services/strategy_service.py`:
- `MarsStrategy.analyze()` → Use `MarketDataProvider.get_daily_history(code, start_year)`
- `CBStrategy.analyze()` → Use `MarketDataProvider.get_latest_price(stock_code)`
- Remove `MarketCache` import
- Update dividend fetching to use `MarketDataProvider.get_dividends()`

## Task 7: Update Admin Router & Main Startup

Modify `app/routers/admin.py`:
- `/api/admin/system/initialize` → Call `MarketDataProvider.warm_latest_cache()`
- Add `/api/admin/market-data/stats` → Return DuckDB row counts, file size, latest date

Modify `app/main.py`:
- `lifespan()` → Replace `MarketCache.get_prices_db()` with `MarketDataProvider.warm_latest_cache()`
- Remove `start_year` logic, `IS_CLOUD` cache limiting (no longer needed)
- Call `market_db.init_schema()` at startup

## Task 8: Revamp Cron Scripts

Update `scripts/cron/`:
- `refresh_current_year.sh` → Verify it works via `backfill_all_stocks()` (auto-aligned)
- `annual_prewarm.sh` → Verify full-year backfill targets DuckDB
- `quarterly_dividend_sync.sh` → Ensure dividend sync writes to DuckDB `dividends` table
- `supplement_prices.py` → Rewrite to UPDATE DuckDB rows directly

## Task 9: Revamp Ops Scripts

Update `scripts/ops/`:
- `verify_integrity.py` → Query DuckDB for coverage gaps instead of scanning JSON files
- `patch_stock_data.py` → UPDATE DuckDB rows instead of patching JSON
- Create `duckdb_stats.py` → Quick health check (row counts, date range, file size)
- Delete `measure_memory.py`, `measure_sqlite_fetch.py` (obsolete)

## Task 10: Full System Verification

Run complete verification:
1. **TSMC CAGR**: From 2006 should be ~19% (same as current)
2. **TSMC Volatility**: Should now use ~5000 daily points (previously 12 monthly)
3. **Race Data**: All 2500+ stocks, 2000-2026 coverage
4. **Dashboard**: Latest prices load < 100ms
5. **RAM Profile**: `resource.getrusage` < 200MB under load
6. **All Crons**: Produce expected output
7. **E2E Tests**: `tests/e2e/e2e_suite.py` passes
8. **Integration**: `tests/integration/test_all_tabs.py` passes

## Task 11: Cleanup & Deploy

After Task 10 passes 100%:
- Delete `app/services/market_cache.py`
- Delete `data/raw/Market_*.json`, `data/raw/TPEx_*.json`, `data/raw/TWSE_Dividends_*.json`
- Remove `race_cache` table from `portfolio.db`
- Update `.gitignore` with `data/market.duckdb`
- Update `Dockerfile` for DuckDB dependency
- Deploy to Zeabur, monitor for 24h

> ⚠️ Do NOT delete JSON files until Task 10 verification passes 100%.
