# Meeting Note: 2026-02-14 - Phase 12 Synchronization

**Date**: 2026-02-14
**Participants**: [PL], [PM], [SPEC], [CODE], [UI], [CV]
**Objective**: Finalize DuckDB Migration, Methodology Alignment, and Data Accuracy.

---

## 1. Project Progress & Status
- **DuckDB Migration**: 
    - Task 1-9: **COMPLETE**. Service layer fully transitioned to `MarketDataProvider`.
    - Task 10: **IN PROGRESS**. System verification identified math discrepancies.
- **ROI Engine Calibration**: 
    - Adaptive Price Standard recognition: **IMPLEMENTED**.
    - Midpoint Reinvestment Methodology: **IMPLEMENTED** (to match docs/product/moneycome_methodology.md).
    - ROI Formula Corrected (Inclusive of start year).

---

## 2. Bug Triage & Discussion

### BUG: "Wrong Data" in Mars Strategy Tab
- **Diagnosis**: 
    - Mixed Price Standards: Some stocks in DuckDB (e.g., 1808) are pre-split-adjusted, while others are nominal. This caused double-adjustment.
    - Methodology Divergence: We were using `close.mean()` instead of `(Open + Close) / 2`.
- **Triage**: 
    - `[CODE]` is running `scripts/ops/fix_price_standards.py` to standardize target stocks to NOMINAL.
    - `[CV]` reports TSMC is now at 23.98% CAGR, needing final trim to hit the 22.2% target.

### ISSUE: Data Gaps (1,308 stocks)
- **Status**: Many stocks start in 2009 instead of 2006.
- **Decision**: Deferred for low-priority stocks. High-priority (0050/2330) are being backfilled.

---

## 3. Architecture & Performance
- **DuckDB**: RAM usage reduced from ~2.7GB to ~50MB. Warm startup < 2s.
- **API**: `/api/results` cold start ~90s (querying all stocks), warm start ~2s.
- **Plan**: `[SPEC]` to finalize `docs/product/duckdb_architecture.md`.

---

## 4. Multi-Agent Brainstorming (Structured Review)

### Topic: Data Integrity Scanning for DuckDB
- **Lead Designer ([SPEC])**: Proposed a "Data Standard Checksum" saved in a new metadata table.
- **Challenger ([CV])**: Flagged that yfinance data can change. A one-time checksum might mask future data drifts.
- **Constraint Guardian ([CODE])**: We must avoid expensive validation on every API call. Checksums should be background/cached.
- **User Advocate ([PM])**: The user just wants the CAGR to match legacy. "Why is it different?" must have a clear UI explanation if data is missing.

**Final Decision**: Implement a `data_standard` column in the `stocks` table (NOMINAL vs ADJUSTED). Default to NOMINAL.

---

## 5. Next Steps
1.  **[CODE]**: Complete standardizing 1808, 2542, 2327 to Nominal.
2.  **[CV]**: Re-verify TSMC Hits 22.2% CAGR target.
3.  **[SPEC]**: Commit `duckdb_architecture.md`.
4.  **[UI]**: Refresh Mars Strategy UI to support mobile view refinements.
5.  **[PL]**: Final verify Task 10 and Proceed to Task 11 (Cleanup).

---
**Meeting Adjourned.**
