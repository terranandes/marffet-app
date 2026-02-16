# Code Review - 2026-02-16

**Topic:** Dividend Migration to DuckDB (Phase 15)
**Reviewer:** [CODE]
**Status:** ✅ Approved

---

## 1. Summary of Changes
- **Objective:** Retire `dividends_all.json` and use DuckDB as the single source of truth for dividends.
- **Scope:** `main.py`, `mars.py`, `market_data_provider.py`, and 6 test files.

## 2. File-by-File Review

### `app/services/market_data_provider.py`
- **Change:** Added `load_dividends_dict(force_reload=False)`.
- **Review:**
    - ✅ **Pattern:** Singleton/Class-level caching (`_dividends_dict`) matches existing `_latest_price_cache` pattern.
    - ✅ **Efficiency:** Loads all dividends in one SQL query (~0.1s) instead of parsing large JSON.
    - ✅ **Fallback:** Handles empty DB gracefully.

### `app/main.py`
- **Change:** Removed `DIVIDENDS_DB` global variable. Replaced with `MarketDataProvider.load_dividends_dict()`.
- **Review:**
    - ✅ **Clean Code:** Removed ~30 lines of hardcoded data and JSON loading logic.
    - ✅ **Safety:** Preserved the exact dict structure `{stock_id: {year: ...}}` so consumers didn't break.

### `app/project_tw/strategies/mars.py`
- **Change:** Replaced `crawler.fetch_ex_rights_history(y)` (Live) with DuckDB read.
- **Review:**
    - ✅ **Performance:** Eliminated 20+ sequential network requests per simulation run.
    - ✅ **Logic:** `stock_divs` construction loop updated correctly for the new data format.
    - ✅ **Safety:** Hardcoded patches (TSMC 2006-2008, etc.) were preserved.

### `tests/*` (6 files)
- **Change:** Updated imports from `app.main` to `MarketDataProvider`.
- **Review:**
    - ✅ **Coverage:** All 6 affected files found via grep were updated.
    - ✅ **Syntax:** Verified with `py_compile`.

## 3. Deployment Notes
- **Critical Dependency:** `market.duckdb` MUST be populated with dividends.
- **Action:** Run `scripts/ops/reimport_twse_dividends.py` immediately after `rebuild_market_db.py` finishes.

---
**Verdict:** Safe to merge.
