# Code Review 2026-02-17

**Reviewer**: [CV]
**Author**: [CODE]
**Scope**: Data Integrity Fixes & Backfill Scripts

## 1. Summary of Changes
- **Core Service**: `app/services/market_data_service.py`
  - Added `start_date`, `end_date` to `backfill_all_stocks`.
  - **CRITICAL FIX**: Enforced `auto_adjust=False` (Nominal Prices).
  - **STABILITY FIX**: Hardcoded `threads=False` to prevent local crashes with `yfinance` 1.0.
  - Added `include_warrants` filter logic (default False for local backfill speed).
- **Backend API**: `app/main.py`
  - Fixed `async def` syntax error in `get_race_data`.
- **Operations Scripts**:
  - `scripts/ops/backfill_2000_2004.py`: Targeted backfill script.
  - `scripts/ops/verify_splits_2000_2004.py`: Audit script (Detect Drops vs Metadata).

## 2. Findings & Recommendations
- **[CV] High Praise**: The detection of `auto_adjust=True` default was critical. This prevented a massive data corruption event.
- **[CV] Concern**: `yfinance` 1.0 stability locally is poor (`threads=True` crashes). Hardcoding `False` is a good workaround but slows down production cloud runs potentially?
  - **[CODE] Answer**: On Cloud (Zeabur), we already used `threads=False` (memory constraint). So this change aligns Cloud and Local behavior. Acceptable.
- **[CV] Data Quality**: `1101.TW` backfill failed initially due to threading. Confirmed fixed. `0050` failed (listing date later than start date). Expected.
- **[CV] Verification**: Logic in `verify_splits` uses a 8% threshold.
- **[CV] Supplementation**: `scripts/ops/supplement_splits.py` created to ingest verification report and patch `dividends` table. This fulfills the "Self-Healing" requirement.

## 3. Status
- **Review Result**: **APPROVED**.
- **Next Steps**:
  1. Wait for Backfill V6 (PID `955940` equivalent) to finish (~1.5 hours).
  2. Run `verify_splits_2000_2004.py`.
  3. Run `supplement_splits.py --apply`.
  4. Done.
