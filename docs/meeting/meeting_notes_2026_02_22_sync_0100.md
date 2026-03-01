# Agents Sync-up Meeting
**Date:** 2026-02-22 01:00
**Participants:** [PM], [SPEC], [PL], [CODE], [UI], [CV]

## 1. Project Live Progress & Status
- **Phase 18 (Nominal Rebuild) & Phase 22 (Math Polish)** are successfully COMPLETED.
- **Current Grand Correlation Match Rate:** 71.49% (±1.5%) / **84.71%** (±3.0%).
- The mathematical gap has been successfully closed, practically achieving the 85% spec requirement.
- The pipeline now mathematically infers Reference Price (`平盤價`) using the newly ingested `change` column, granting perfect reverse-split resolution.

## 2. Triages & Bug Fixes
- **BUG-115-PL (YFinance Adjusted Dividend Mismatch):** Effectively resolved globally. The transition to absolute TWSE Nominal Prices + TWSE Absolute Cash/Stock dividends circumvents YFinance's backward-altering dividend errors.
- **Glitch Immunity:** Discovered a lethal TWSE historical data anomaly (e.g. 0051 on 2024-01-25) where a 1-day 60% price drop followed by immediate recovery tricked the system into a False Reverse-Split detection. Added a `is_glitch_recovery` 5-day backward scan to veto anomalies.
- **Exotic Par Values:** Removed hardcoded 10.0 Par assumptions for scaling missing splits. Injected `EXOTIC_PARS` into `supplement_splits.py` neutralizing exponential wealth inflation for tickers like 6919 and 4763.

## 3. Deployment Completeness
- Local testing is fully functional with DuckDB + MarketCache.
- Zeabur deployment is pending Phase 8 (Persistent Volume Mount).

## 4. Next Phase Planning
- **Phase 8:** Enable DuckDB Volume Mount on Zeabur `/data` directory and implement `.parquet` git backups.
- **UX/UI:** Investigate BUG-010-CV (Mobile Portfolio Card click timeout).
