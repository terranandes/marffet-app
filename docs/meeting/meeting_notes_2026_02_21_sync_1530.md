# Meeting Notes: 2026-02-21 Afternoon Sync-up (15:30H)

**Date**: 2026-02-21
**Attendees**: [PM], [SPEC], [PL], [CODE], [UI], [CV], [Terran/Boss]
**Topic**: Phase 18 Pipeline Recovery & Database Rebuild Status

## 1. Project Live Progress
- **Phase 18 (Nominal Rebuild)**: Active. The system is currently inserting 5 million pure nominal price records into DuckDB. 
- **DB Rehydration Speedup**: [CODE] and [PL] optimized `rebuild_market_db.py`. By dropping the B-Tree primary key constraints and performing raw bulk insertions (`INSERT INTO ... SELECT * FROM _tmp_nominal` instead of `ON CONFLICT DO UPDATE`), the process of loading 22 years of daily data was reduced from ~10 hours to ~15 minutes.
- **Current Completion**: The DuckDB rebuild is crossing into **mid-2017 (roughly 60% complete)**. 

## 2. Bug Triages & Pipeline Incidents
- **Rogue Script Incident (`recovery_goodinfo.py`)**: 
  - **Issue**: Attempted to use `recovery_goodinfo.py` to ingest absolute dividends. However, this script contained a hardcoded `DELETE FROM daily_prices`, which wiped the fully constructed 5-million row database. It also needlessly spawned Playwright instances.
  - **Resolution**: Escaped the script. Restarted the nominal DB rebuild. The pipeline in `docs/product/tasks.md` was updated to use the correct `reimport_twse_dividends.py` script for Step 3, which safely maps Goodinfo KY-patches without touching price data.
- **The "區分權息" Challenge**: 
  - Logged as an open issue. The TWSE absolute dividend data sometimes conflates cash (息) and stock (權) dividends on the same day. 
  - **Strategy**: Will use mathematical price drop detection (`supplement_splits.py`) over the nominal prices to cross-verify and tease apart stock splits from cash dividends.

## 3. Product Rules & Features
- **Strict 2004+ Timeline Requirement**:
  - Boss (Terran) formalized the rule that the Mars Simulation tabular data will only support 2004 and onwards.
  - **Rationale**: YFinance data from 2000-2003 automatically, retroactively adjusts historical dividends upon modern stock splits. This completely bankrupts the mathematical integrity of the MoneyCome simulation engine (triggering the double-slicing fallacy). 2004 is the hard cutoff because it aligns with the absolute limit of pristine TWSE MI_INDEX digital archives.

## 4. UI/UX Review
- **BUG-114-CV**: Mobile Portfolio Card Click Timeout pending investigation. [UI] will hold off on frontend tasks until the backend correlation recovers.

## 5. Next Actions
- [PL] Monitor the DuckDB bulk insertion until 2025 is reached.
- [PL] Execute `scripts/ops/reimport_twse_dividends.py` to overlay absolute TWSE cash and stock dividends.
- [PL] Execute `scripts/ops/supplement_splits.py --apply` to mathematically synthesize stock splits.
- [CV] Run the `tests/analysis/correlate_all_stocks.py` pipeline to verify the target >85% match rate against MoneyCome.
