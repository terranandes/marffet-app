# Ralph Loop: Data Verification (MoneyCome Correlation)
**Objective**: Verify the "Ultra-Fast Crawler" data (MarketCache V2) against MoneyCome benchmarks to ensure accuracy.

**Status**: [INIT]

## 1. Context
- **Previous State**: We trusted yfinance (slow, sometimes inaccurate).
- **Current State**: We implemented "Ultra-Fast Crawler" using official TWSE/TPEx data (MarketCache V2).
- **Gap**: We never formally "correlated" this new data source against our Golden Standard (MoneyCome).

## 2. Tasks
1.  **[CODE] Create Verification Script**:
    -   Script: `tests/verify/verify_moneycome_correlation.py`
    -   Inputs: List of key stocks (Types: Large Cap, SNP, ETF, High Volatility).
        -   2330 (TSMC)
        -   0050 (ETF)
        -   2412 (Chunghwa Telecom)
        -   **New**: 00937B (Bond ETF - Check if we handle it)
    -   Logic:
        -   Run `ROICalculator` using `MarketCache` (New Data).
        -   Compare Result (CAGR, Final Wealth) vs MoneyCome (Manual/Known benchmarks).
2.  **[CV] Execute & Analyze**:
    -   Run the script.
    -   Identify discrepancies > 1%.
3.  **[CODE] Fix Data/Logic**:
    -   If discrepancy found: Is it Data (Price) or Logic (Dividend Reinvestment)?
    -   Fix in `market_cache.py` or `calculator.py`.
4.  **[PL] Sign-off**:
    -   Update `specifications.md` with "Verified against MoneyCome using Crawler V2 Data".

**Success Criteria**:
-   TSMC 2006-2025 CAGR matches MoneyCome within 0.5%.
-   0050 2006-2025 CAGR matches MoneyCome within 0.5%.
