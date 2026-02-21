# Code Review Note
**Date:** 2026-02-22 01:00
**Reviewer:** [CV]

## 1. Changes Reviewed
- `app/services/split_detector.py`: Approved the transition from `curr_open` to mathematically-precise `curr_close - curr_change` for calculating the Reference Price. This removes floating-point inaccuracies when isolating forward/reverse splits.
- `app/services/split_detector.py`: Approved the addition of the 5-day `is_glitch_recovery` lookback logic, which accurately suppresses artificial reverse split detection resulting from V-shape data anomalies (e.g., 0051 ETF).
- `scripts/ops/supplement_splits.py`: Confirmed that applying the dynamic `EXOTIC_PARS` mapping to historical ratio recovery accurately standardizes artificial stock dividends for non-standard par companies (e.g., 6919, 4763). This fixed the 256% CAGR runaway multiplication bug.
- `app/services/market_db.py` & `recover_db.py`: Verified schema backward-compatibility when inflating the DuckDB table with the new `change DOUBLE` column.

## 2. Performance & Security
- DuckDB nominal ingestion via Pandas zero-copy remains highly performant (~14 mins for 20 years).
- Split detection loop logic is optimal; `0(1)` dictionary lookup for `EXOTIC_PARS` poses zero runtime overhead.

## 3. Discrepancy (Local vs Deployment)
- Changes are fully validated against local dataset. 
- Deployment to Zeabur will require pushing the generated DuckDB `.parquet` snapshots.
