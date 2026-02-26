# Code Review Note
**Date:** 2026-02-27 01:30 HKT
**Reviewer:** [CV]

## 1. Changes Since Last Review
- **`roi_calculator.py`:**
  - `start_year` offset fixed for the baseline history entry: it is now recorded as `start_year - 1` rather than duplicating the first active simulation year's tag.
  - This solves the BCR front-end display bug where 2N entries existed for Year 1, skewing the graph.

## 2. Mathematical Integrity Review
- **Discrepancy Investigation:** End-User reported a TSMC 2006 value discrepancy against the legacy MoneyCome reference. 
- **MoneyCome Logic:** Mathematical reconstruction reveals MoneyCome generated exactly 40,969 Cash Dividends in 2006 for a $1.06M capital layout across *all* entry timings (Open/High/Low). This points to an execution-price-agnostic logic for Year 1 dividends in their older unadjusted engine.
- **Martian Engine Logic:** Our new `ROICalculator` is dynamic and computes precise dividend share bases directly linked to the specific strategy's execution price (BAO, BAH, BAL). 
- **Verdict:** Our computation is technically more robust and mathematically accurate for strategy differentiation. We intentionally reject replicating the MoneyCome hardcoded Year 1 reference layout. 

## 3. Deployment Parity
- Verified identical performance running the DuckDB streaming query across `localhost` and `Zeabur`. 
- Data pipeline is perfectly replicated; Parquet rehydration functionality works correctly.

## 4. Verdict
- **Production Code:** APPROVED.
- **Data Integrity:** VERIFIED. No regressions injected.
- **Data Discrepancy Action:** Deferring legacy MoneyCome matching in favor of improved execution-price mapping.
