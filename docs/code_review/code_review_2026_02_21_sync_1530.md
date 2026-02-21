# Code Review Notes: 2026-02-21 Afternoon Sync-up (15:30H)

**Date**: 2026-02-21
**Reviewers**: [CV], [CODE], [PL]
**Topic**: DuckDB Mass Insertion Optimization & Pipeline Verification

## 1. DuckDB B-Tree Optimization (`fetch_mi_index_mass.py`)
**Changes Made:**
- Temporarily eliminated the `UNIQUE(stock_id, date)` constraint and Primary Key during schema generation for Phase 18, Step 2.
- Modified `flush_to_db` from an Upsert (`ON CONFLICT (stock_id, date) DO UPDATE SET...`) to a raw bulk insert (`INSERT INTO daily_prices SELECT * FROM _tmp_nominal`).

**[CV] Assessment:**
- **Status: APPROVED**.
- **Reasoning**: Upserting 5 million records into an indexed DuckDB file caused massive B-Tree rebalancing and disk thrashing, dragging the process out to 10+ hours. Since we are rebuilding from a clean, mathematically deduplicated set of daily JSON files, zero-conflict insertion is guaranteed. The `O(1)` sequential write speedup (15 minutes total) is a mandatory architectural change for local rebuilds. 
- **Follow-up Action**: After Phase 18 Step 4 finishes, we must run a SQL command to re-establish the Index/Primary Key on the database for rapid querying by the UI backend.

## 2. Rogue Script Identification (`recovery_goodinfo.py`)
**Changes Made:**
- Discovered that `recovery_goodinfo.py` actively executes `DELETE FROM daily_prices` on boot, wiping the database.
- Removed `recovery_goodinfo.py` from the Phase 18 pipeline documented in `tasks.md`.

**[CV] Assessment:**
- **Status: REJECTED usage of `recovery_goodinfo.py`**.
- **Reasoning**: This script was an outdated workaround designed to scrape daily highs/lows from Goodinfo for missing stocks, and it destructively resets the DB. 
- **Corrected Path: APPROVED `reimport_twse_dividends.py`**. This script intelligently reads the massive `dividends_all.json` cache and applies the Goodinfo JSON patches to KY/DR stocks via `INSERT INTO dividends`, safely isolating the step from `daily_prices`.

## 3. Review Conclusion
The codebase is currently stable. The pipeline logic has been corrected to prevent accidental data wiping. Awaiting next steps for dividend injection.
