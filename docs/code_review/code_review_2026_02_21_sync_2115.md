# Code Review Note
**Date:** 2026-02-21 21:15
**Reviewer:** [CV]

## 1. Changes Reviewed
- `app/services/split_detector.py`: Reviewed the removal of the noisy reverse split auto-detection. Approved the implementation of the Pre-Spike Stability Check (`i >= 2`) which successfully prevents L-shape logic from triggering on V-shape data glitches.
- `app/project_tw/calculator.py`: Approved the calculation logic `yr_split != 1.0` allowing capital reductions to factor into the ROI without breaking forward split multiplication.
- `tests/analysis/correlate_all_stocks.py`: The `ref_yrs_count` argument passing is mathematically sound. The exclusion `if ref_yrs_count > years_available + 1.5:` is the correct heuristic to exclude Emerging Market (興櫃) crossovers without accessing the 興櫃 API database.

## 2. Performance & Security
- DuckDB B-Tree bypass logic is performing exceptionally well, dropping millions of rows in minutes. Memory leaks and disk thrashing on insertions have been resolved.
- Correlation script execution has been stabilized. Floating-point accuracy is preserved by adhering strictly to TWSE base limits.

## 3. Discrepancy (Local vs Deployment)
- Local environment is clean and running perfectly.
- Zeabur environment requires Volume mount.
