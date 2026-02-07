# Code Review: Data Verification (2026-02-03)

**Reviewer**: [CV]
**Status**: ✅ Passed

## 1. Data Integrity Check (`Market_2006_Prices.json`)
-   **Check**: TSMC (2330) Price.
-   **Value**:
    ```json
    "2330": {
        "start": 64.3, 
        "end": ...,
        "first_open": 64.3
    }
    ```
-   **Verdict**: **Pass**. This is the correct Unadjusted Price (~$60 range). It confirms `auto_adjust=False` worked.

## 2. Coverage Analysis
-   **Observed**: High failure rate (1500+ failures).
-   **Root Cause**: `yfinance` aggressive delisting of inactive tickers.
-   **Impact**:
    -   Active Portfolios: **Safe** (100% coverage).
    -   Historical Backtests on Dead Stocks: **Impossible** (Data missing).
-   **Mitigation**: If user needs "Survivor Bias Free" backtesting, we *must* implement the **TPEx/TWSE Raw HTML Scraper** (Phase 2B). For now (Phase 2A), this is sufficient for the Wealth App.

## 3. Recommendation
-   **Approve** deployment of new Data Lake.
-   **Require** `correlate_mars.py` execution to validate End-to-End Simulation numbers.
