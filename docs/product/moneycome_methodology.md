# MoneyCome Methodology & Verification

## Objective
The goal is to replicate the ROI (Return on Investment) simulation logic provided by the popular Taiwanese site **MoneyCome.in**. This serves as our "Golden Master" for verifying the accuracy of our backtesting engine.

## Core Logic (Re-Engineered)
Based on `tests/debug_tools/sim_moneycome.py` and comparative analysis.

### 1. Simulation Parameters
- **Principal**: Initial lump sum investment (e.g., 1,000,000 TWD).
- **Annual Contribution**: Yearly addition to capital (e.g., 60,000 TWD).
- **Dividend Policy**: **100% Reinvestment**. All cash dividends are used to buy more shares.
- **Timeframe**: Typically 2006 - Present (20 years).

### 2. Execution Steps (Per Year)
1.  **Jan 1st**: Start of Year Price.
2.  **Dividend Distribution**:
    -   Lookup Cash Dividend ($D$) for the year.
    -   `Total Dividends = Current Shares * D`.
3.  **Reinvestment & Contribution**:
    -   Assumption: The user buys shares throughout the year.
    -   **Reinvestment Price**: `Average Price = (Start Price + End Price) / 2`.
    -   `New Shares (Div)` = `Total Dividends / Average Price`.
    -   `New Shares (Contrib)` = `Annual Contribution / Average Price`.
4.  **Dec 31st**: End of Year Price. Update Total Value.

### 3. Data Sources
-   **Price History**: `daily_prices` (DuckDB). **Mandatory: 100% Nominal Basis**. Adjusted prices (TRI) are strictly forbidden as they cause "Double Adjustment" errors.
-   **Dividends**: `dividends` (DuckDB). Nominal cash and stock dividends.

### 4. Verification Benchmark
**Target**: TSMC (2330)
-   **Period**: 2006 - 2025
-   **CAGR Target**: **22.2%** (±0.1%)
-   **Validation Script**: `tests/e2e/test_universal_data.py` (Asserts this value).

## Key Differences from Legacy Logic
-   **Legacy (Project TW)**: Often bought at "First Close". did not always average the price for reinvestment.
-   **New (MoneyCome)**: Uses `(Start + End) / 2` approximation for DCA (Dollar Cost Averaging) effect.
