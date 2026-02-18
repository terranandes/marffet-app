# Martian Sync-Up Meeting 🛰️ (2026-02-17 v4)

**Date**: 2026-02-17
**Time**: 05:05 HKT
**Participants**: [PM], [SPEC], [PL], [CODE], [UI], [CV]
**Meeting Status**: **Data Integrity Siege (2000-2004)**

## 1. Project Progress
- **Backfill V4 (Active)**: 
  - [PL] "We are executing a surgical backfill for the 2000-2004 gap using `yfinance`."
  - [CODE] "Optimized with `threads=False` (Local Stability) and `include_warrants=False` (Speed). ETA 1.5 hours."
- **Verification System**:
  - [CV] "Script `verify_splits_2000_2004.py` is ready. Initial tests on partial data confirmed it successfully flags missing splits (e.g. 2317) and mismatches (e.g. 2454)."

## 2. Bug Triage & Fixes (Critical)
- **BUG-014: Double-Counting Dividends**: 
  - **Issue**: `backfill_all_stocks` was using `yfinance` default (`auto_adjust=True`), importing Adjusted Prices *and* Dividend records. This would cause `ROICalculator` to double-count returns.
  - **Fix**: [CODE] Enforced `auto_adjust=False` to fetch Nominal Prices.
- **BUG-015: Local Backfill Crash**:
  - **Issue**: `yfinance` 1.0 multi-threading causes silent process exit on local env.
  - **Fix**: [CODE] Forced `threads=False` in `market_data_service.py` for stability.
- **BUG-016: Server Startup Crash**:
  - **Issue**: `get_race_data` used `await` but was defined as `def`.
  - **Fix**: [CODE] Changed to `async def`.

## 3. Discrepancy & Verification
- **2000-2004 Gap**: 
  - [PL] Confirmed valid backfill is filling this gap.
  - [CV] Found data quality issues in `yfinance` source (e.g., missing cash dividends, weird split ratios). We will need to patch these using the Verification Report.

## 4. Worktree Status
- **Branch**: `master` (Clean, ahead of origin by ~60 commits).
- **Recent Commits**: `ac79a5e` (fix backfill adjustment).

## 5. Action Items
- [PL] Monitor Backfill V4 completion.
- [CV] Run `verify_splits_2000_2004.py` on full dataset.
- [CODE] Generate `import_splits.py` to patch missing records based on verification report.
- [ALL] Verify "2000-Current" integrity before declaring success.
