# Crawler Architecture & Performance Review

**Status**: [CODE] Implementation Review
**Date**: 2026-02-14 (Updated for Phase 12)
**Module**: `app/project_tw/crawler.py`, `scripts/ops/reimport_twse_dividends.py`

## 1. Overview
The Marffet Crawler is designed for **Market-Wide Batch Analysis**. It prioritizes **Nominal Data Accuracy** over speed, ensuring that the backtesting engine processes valid historical dividends without "Adjusted Close" distortion.

### Key Components
- **`StockInfoService`**: O(1) Fetcher for official TWSE/TPEX stock list & names.
- **`fetch_mi_index_mass.py`**: **[PRIMARY PRICE]** Heavy-lifting batch processor ingesting absolute pristine nominal daily prices directly from official TWSE JSON snapshots 2004-Present to populate DuckDB.
- **`Hybrid Dividend Crawler`** (`scripts/ops/reimport_twse_dividends.py`): 
  - **Primary**: Fetches nominal dividends from TWSE TWT49U (2003-Present).
  - **Fallback**: Applies hardcoded patches for outliers (e.g., 2327, 1808) and pre-2003 data gaps.
- **DuckDB**: Primary storage for all crawled data (`market.duckdb`), replacing raw JSON files for production queries.

### Tech Stack
- **AsyncIO / HTTPX**: Concurrency and connection pooling.
- **DuckDB**: Analytical OLAP database for high-performance querying.
- **Pandas**: Data transformation before DB insertion.

## 2. Dividend Strategy: Hybrid Approach (Phase 12)
We moved away from `yfinance` adjusted dividends due to double-counting issues. The new strategy is:

### A. Primary Source (2003-Present)
- **Endpoint**: `https://www.twse.com.tw/exchangeReport/TWT49U`
- **Logic**:
  - Fetches data by Year/Quarter.
  - Parses `Cash Dividend` and `Stock Dividend` columns strictly.
  - **Fixes**: 
    - Handles mixed `float/string` types in older schemas (2003-2008).
    - Ignores "Adjusted" columns to preserve Nominal values.

### B. Fallback & Calibration
- **Outliers**: Specific stocks like **1808 (Run Long)** have complex "Rights + Cash" events that simpler parsers misinterpret. We use a **Patch Map** to force correct values.
- **TSMC (2330)**: Specific 2006-2009 stock dividends differ between TWT49U derivation and official records. We patch these to ensure the benchmark CAGR aligns with reality (~24.18%).
- **Pre-2003**: TWSE data is sparse. We use a fallback dictionary to fill critical gaps for backtesting start dates.

## 3. Performance Analysis

### A. Concurrency strategy
*   **Sizing**: `asyncio.Semaphore(4)` for TWSE to avoid IP bans (approx 1.5s delay).
*   **Throughput**: 
    *   Full Dividend History (2003-2025): ~90 requests.
    *   Execution Time: ~2-3 minutes (sequential year batches).

### B. Storage & Caching
*   **Raw Cache**: `data/raw_dividends/TWSE_Dividends_{YYYY}.json` (Persisted to minimize network hits).
*   **Production**: Data is inserted into DuckDB `dividends` table.
    *   Query Speed: < 5ms for full stock dividend history.

## 4. Recommendations
1.  **Live Fallback**: Replace hardcoded patches with a live scraper for **Goodinfo** or **Yahoo Finance** (Nominal Mode) to handle future outliers automatically.
2.  **Cron Integration**: Ensure `scripts/cron/` jobs use the new `MarketDataProvider` to keep DuckDB up-to-date daily.
