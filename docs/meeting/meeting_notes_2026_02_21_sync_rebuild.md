# Meeting Notes: 2026-02-21 Pre-Rebuild Sync-up (03:13H)

**Date**: 2026-02-21
**Attendees**: [PM], [SPEC], [PL], [CODE], [UI], [CV], [Terran/Boss]
**Topic**: Phase 18 Database Rebuild & Final Verification Protocol

## 1. Project Live Progress
- **Phase 17 Results**: The Grand Correlation run dropped from >80% to 30.5% Match Rate. 
- **Root Cause**: Two factors. 
  1. The "Bankrupt Terminal Math" fallacy in `calculator.py` forced $0 values for M&A stocks (e.g. SPIL 2325), crashing their CAGR to -100%. This was reverted this morning.
  2. The DuckDB is heavily corrupted by YFinance adjusted data fetching (BUG-115).
- **Current State**: `docs/product/tasks.md` has been updated with Phase 18: Pure Nominal Database Rebuild. The data pipeline scripts are ready.

## 2. Bug Triages & Jira
- **✅ BUG-116-CODE**: TPEx Native API Silent Date Fallback. Fixed by using YFinance bounds.
- **🔴 BUG-115-PL**: YFinance Adjusted Dividend Mismatch. Confirmed as the root cause of the correlation failure. We must abandon YFinance for primary dividend/price building and rely strictly on Nominal MI_INDEX data and isolated TWSE dividend records.
- **🟡 BUG-010-CV**: Mobile Portfolio Card Click Timeout pending investigation by [UI].

## 3. Features & Deployment Status
- **Phase 18 Pipeline**: Ready to execute. We will wipe the 500MB+ `market.duckdb` and generate a pristine nominal database.
- **Zeabur Persistence**: The DuckDB Volume Mount remains the sole remote blocker. Pushing a highly correlated DB via Parquet backup is required to finalize Zeabur deployment.

## 4. UI/UX Review
- [UI]: Focus continues to be deferred until the backend correlation recovers back to >85%.

## 5. Worktree Flow & Branch Status
- The `master` branch contains the reverted/fixed `calculator.py` logic which properly freezes M&A terminal values instead of defaulting to 0.
- Numerous recovery scripts are scattered in `/scripts/ops`. Post-Phase 18, we will need to aggregate these into a clean `/tests/debug_tools` toolkit or remove the redundant json parsers.

## 6. Multi-Agent Brainstorming & Adjustments
- **[PM] & [SPEC]**: Conducted a thorough brainstorm documented in `docs/brainstorming/brainstorm_2026_02_21_correlation_recovery.md`. 
- **Consensus**: We must establish "Ground Truth". Ground truth is unadjusted nominal prices + absolute TWSE dividend entries + mathematically detected splits.
- **Timeline Rule**: Boss (Terran) has officially decreed that the Mars Simulation and overall system timeline is restricted to **2004+**. All YFinance data from 2000-2003 is permanently discarded because YFinance retroactively alters historical dividends/prices upon stock splits, which mathematically corrupts the MoneyCome simulation engine.

## 7. Next Actions
- [PL] report to Terran.
- Await the green light to initiate the Phase 18 script chain:
  `recover_db.py` -> `recovery_sequential.py` -> `recovery_goodinfo.py` -> `supplement_splits.py` -> `correlate_all_stocks.py`.
