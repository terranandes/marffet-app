# Code Review: Hybrid Dividend Crawler (Phase 12)

**Reviewer**: [CODE]
**Date**: 2026-02-14
**Target Files**:
1. `scripts/ops/reimport_twse_dividends.py`
2. `app/project_tw/crawler.py`

## 1. Summary
The implementation successfully shifts the dividend data source from `yfinance` double-counting to a nominal `TWSE + Fallback` model. This is critical for the "MoneyCome Methodology" alignment.

## 2. Findings

### A. `app/project_tw/crawler.py` (TWT49U Parser)
- **Improvement**: Added robust type checking `isinstance(val, str)` for `Prior`, `Ref`, `Cash`, `Stock` columns.
- **Context**: The TWT49U API returns inconsistent types (float vs string) across different years (e.g., 2005 vs 2024). The previous code crashed on `float.replace()`.
- **Status**: **Approved**.
- **Observation**: The parser correctly ignores "Adjusted" dividend columns which were causing the inflation.

### B. `scripts/ops/reimport_twse_dividends.py`
- **Architecture**: Sequential Year-by-Year fetching.
- **Fallbacks**:
  - `FALLBACK_PATCHES` dictionary handles:
    - Pre-2003 data (TWSE unavailable).
    - Outlier 1808 (Run Long) Combined Dividends.
    - TSMC 2006-2009 Stock Dividends (Correction of derivation error).
- **Concurrency**:
  - Uses `duckdb.connect()` context manager.
  - **Issue**: Encountered locking conflicts with running web server.
  - **Resolution**: Previously resolved via `fuser -k`.
  - **Recommendation**: Ensure the application is stopped or DuckDB is in read-only mode for large batches if concurrency becomes a persistent issue.

### C. Data Integrity
- **1808**: Confirmed fix from 66.55 -> 3.0/1.2.
- **2330**: Confirmed fix of stock dividend overshoot.

## 3. Action Items
- Monitor `cron` job logs to ensure `reimport` automation works if scheduled.
- Consider moving `FALLBACK_PATCHES` to a config file or database table in Phase 13.

**Verdict**: **LGTM (Looks Good To Me)**. Ready for Grand Correlation.
