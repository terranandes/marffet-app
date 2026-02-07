# Technical Specification: Mars Strategy Revamp & Universal Data Lake

**Status**: Approved
**Date**: 2026-02-02
**Related Tasks**: Mars Strategy Correlation, Universal Data Lake

## 1. Executive Summary
We are refactoring the "Mars Strategy" engine to achieve **Clean Room Correlation** with MoneyCome (Golden Excel). Instead of patching the output, we will implement the correct "Physics" of the simulation using **Universal Raw Data**.

## 2. Architecture: Dual Database Strategy
To support high-performance simulations and cross-tab reuse (BCR, Portfolio, Cash Ladder), we will separate user state from market data.

| Feature | Portfolio DB (`portfolio.db`) | Market Data Lake (`market_data.duckdb` / `.parquet`) |
| :--- | :--- | :--- |
| **Content** | User Profiles, Portfolios, Transactions, Notifications | **Raw** Daily OHLCV, Corporate Actions (Splits, Divs) |
| **Source** | User Input / App Logic | TWSE/TPEx Crawler |
| **Persistence** | Zeabur Volume (Persistent) | Zeabur Volume (Persistent) |
| **Backup** | **Git Tracked** (via `backup.py` dump) | **Not Git Tracked** (Rebuilt on-fly from Scratch) |
| **Granularity** | Transaction Level | Daily (2006-Present) |

## 3. "Physics" Engine Specification
The simulation engine (`ROICalculator`) must operate on **Unadjusted Prices** to correctly simulate historical capital deployment.

### 3.1 Core Principles
1.  **Unadjusted Prices**: $1M invested in 2006 buys shares at 2006 market price (e.g., $60), not split-adjusted price ($10).
2.  **Event-Driven Adjustments**:
    -   **Stock Dividend**: `Shares *= (1 + stock_div/10)`. Price drops naturally on Ex-Date.
    -   **Stock Split**: `Shares *= Ratio`. `Price /= Ratio`.
    -   **Capital Reduction**: `Shares *= (1 - Ratio)`. `Cash += Shares * CashReturn`. (User Rule: Ignore Cash).
3.  **Buy Logic Flexibility**:
    -   `timing`: **First Day** vs **High** vs **Low**.
    -   `price`: **Open** vs **Close**.
    -   *MoneyCome Single Mode*: First Day / Closing Price.
    -   *MoneyCome Comparison*: Supports High/Low options.

## 4. Implementation Plan

### Phase 1: Engine Refactor (`calculator.py`)
-   [ ] **Purge**: Remove `if stock_code == '2330'` hardcoded overrides.
-   [ ] **Parametrize**: Add `buy_logic` (First/High/Low) and `price_type` (Open/Close).
-   [ ] **Events**: Add `handle_corporate_actions` method.

### Phase 2: Universal Data Lake (Crawler)
-   [ ] **Format**: Switch storage from JSON/CSV to **Parquet**.
-   [ ] **Crawler**: Update `TWSECrawler` to fetch Daily OHLCV + Corporate Actions.
-   [ ] **Optimization**: Use `polars` or `duckdb` for instant querying.

### Phase 3: Correlation & Verification
-   [ ] **Correlator Script**: Run global simulation using the new engine. on `market_data`.
-   [ ] **Compare**: Verify CAGR matches MoneyCome within 0.5% margin.
