# Code Review: 2026-02-21 Pre-Rebuild Sync-up

**Date**: 2026-02-21
**Reviewer**: [CV]
**Scope**: Calculator M&A Freeze Logic Reversion

---

## 1. Changes Reviewed
### 1.1 `app/project_tw/calculator.py` (L297-L327)
**Purpose**: Fixing the terminal evaluation for stocks that disappear from the exchange (Acquisitions, Mergers, Bankruptcies) prior to the 2026 target correlation year.
**Issue**: An earlier patch forced `terminal_value = 0.0`. This ruined the correlation for acquired companies, which MoneyCome evaluates based on their buyout/final traded price.
**Fix Assessment**: ✅ APPROVED. [CODE] successfully refactored the early exit loop. 
- `terminal_value = total_asset_value` freezes the value.
- `cagr_raw` and `roi_raw` now evaluate the frozen terminal value against the frozen `total_invested_cash`.
- The simulation timeline correctly persists output keys out to `s2006e2026bao` without falsifying a total loss unless the asset value was genuinely 0.

## 2. Process Assessment
- **Data Pipeline Scripts**: Reviewing `scripts/ops/recovery_sequential.py` and `scripts/ops/recover_db.py`. They correctly implement DuckDB constraints and target the pure `/data/raw_test/MI_INDEX` JSONs.
- **Split Detection**: `supplement_splits.py`'s math (>40% drop = split multiplier) is verified to safely mutate the `dividends` table exclusively. No price adjustments.

---
**Signed**: [CV] Code Verification Agent
