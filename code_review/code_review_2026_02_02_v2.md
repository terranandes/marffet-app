# Code Review: Data Quality & Probe Analysis (v2)

**Date**: 2026-02-02
**Reviewer**: [CV] (Code Verification)
**Scope**: `calculator.py`, `probe_*.py`, Data Integrity

---

## 1. 🔍 Logical Review: `app/project_tw/calculator.py`
- **Rating**: ✅ **Pass (Logic)** / ❌ **Fail (Data Safety)**
- **Analysis**:
    - The `ROICalculator` correctly implements "Buy Shares = Cash / Price" and "Add Shares = Shares * StockDiv".
    - **Vulnerability**: It has no safeguards against **Adjusted Prices**. If `price` input is artificially low (due to split adjustments), the `shares_bought` becomes artificially high.
- **Recommendation**:
    - Add a **Sanity Check**: For known large caps (TSMC), warn if Start Price < $40 (Impossible in 2006).
    - Or, enforce a metadata flag `is_unadjusted=True` in the Data Lake nodes.

## 2. 🧪 Probe Analysis: `tests/probe_yfinance.py`
- **Result**: `Success`.
- **Finding**:
    ```python
    # code output
    Open: 59.106... (auto_adjust=False)
    Adj Close: 29.496...
    ```
- **Implication**: `yfinance` *can* provide the correct data. The current Data Lake was effectively "poisoned" by default settings.
- **Action**: Future ingestion *must* strictly use `auto_adjust=False`.

## 3. 📉 Coverage Review: `scripts/correlate_stocks.py`
- **Result**: 98.92% on Filtered List.
- **Verdict**: The "Coverage" is excellent. The "Gap" in the Unfiltered list is acceptable (Delisted/Emerging). The real issue is **Data Definition** (Price Adjustment), not Coverage.

## 4. 🚀 Directive
**Reject** current Data Lake release.
**Require** full re-ingestion with **Unadjusted Prices** (via Official Scraper or Configured Client).
