# Crawler Architecture & Performance Review

**Status**: [CODE] Implementation Review
**Date**: 2026-01-16
**Module**: `app/project_tw/crawler.py`, `app/project_tw/strategies/mars.py`

## 1. Overview
The Martian Crawler is designed for **Market-Wide Batch Analysis** rather than single-stock fetching. Instead of making 20 years x 12 months x 1000 stocks (240,000 requests) to fetch history, it primarily uses **Market Daily Quotes (MI_INDEX)** to snapshot the entire market at the start and end of each year.

### Key Components
- **`StockInfoService`**: **[NEW]** O(1) Fetcher for official TWSE/TPEX stock list & names (Dynamic Naming).
- **`TWSECrawler`**: Handles TWSE (Exchange) interactions.
- **`TPEXCrawler`**: Handles TPEx (OTC) interactions.
- **`MarsStrategy`**: Orchestrates the "Market-Wide" data fetching and in-memory association.

### Tech Stack
- **AsyncIO**: Python's `asyncio` for concurrency.
- **HTTPX**: `httpx.AsyncClient` for non-blocking HTTP requests with HTTP/2 support (optional) and connection pooling.
- **Pandas**: In-memory data manipulation.
- **Local File Cache**: JSON-based file persistence in `data/raw`.

## 2. Performance Analysis

### A. The "Market-Wide" Optimization
*   **Standard Approach**: Fetch stock `A` (2006-2025), Fetch stock `B`...
    *   *Complexity*: O(Stocks × Years × Months)
    *   *Requests*: ~240,000 for full market.
*   **Martian Approach**: Fetch **Market Snapshot** for Jan 2 and Dec 31 of each year.
    *   *Complexity*: O(Years)
    *   *Requests*: 20 Years × 2 Dates = **~40 requests total**.
    *   *Result*: We get Start/End prices for **ALL** listed stocks instantly.

### B. Parallelism & Concurrency
*   **Sizing**: 
    *   `asyncio.Semaphore(50)`: Limits CPU-bound processing concurrency.
    *   `asyncio.Semaphore(4)`: Limits IO-bound polling per server (to avoid IP bans).
*   **Chunking**:
    *   The crawler fetches data in chunks of **Years** or **Quarters** (for Dividends) to respect API response size limits.
    *   `fetch_market_prices_batch`: Returns a dictionary mapping `{year: {stock_code: data}}`.

### C. Bottlenecks
1.  **Deep Scan (Split Detection)**:
    *   When the strategy detects a price drop > 65% (suspected stock split), it triggers `detect_daily_split`.
    *   **Cost**: This reverts to fetching **12 months of daily data** for that specific stock-year.
    *   *Impact*: If 50 stocks split in a year, we make 50 × 12 = 600 extra requests.
2.  **Rate Limiting**:
    *   TWSE is strict. We enforce `await asyncio.sleep(0.5)` to `1.5` between requests.
    *   This sets a hard floor on speed (~1-2 requests/sec).

### D. Time Estimation
*   **Cached Run**: < 5 seconds (All data loaded from SSD).
*   **Cold Run (First Time)**: 
    *   Market Prices: ~40 reqs × 1.5s = **60 seconds**.
    *   Dividend Data: 20 years × 4 quarters = 80 reqs × 1.5s = **120 seconds**.
    *   **Total**: ~3 minutes to construct the entire 20-year database for ALL stocks.

## 3. Caching & Stale Data Logic

### Current Mechanism
*   **Storage**: JSON files in `project_tw/data/raw/` (e.g., `Market_2024_Prices.json`, `2330_20241201.json`).
*   **Hit Logic**: If file exists, read it. **No expiration check.**

### Critical Gap: Current Year Data
*   **Problem**: If `Market_2026_Prices.json` was created on Jan 1st, and today is Jan 16th, the crawler returns the Jan 1st file. It **does not** auto-refetch the current partially-complete year.
*   **Fix Required**:
    *   Identify "Closed" years vs "Current/Open" year.
    *   For `Current Year` (e.g., 2026), **Bypass Cache** or **Expire Cache** (e.g., > 24 hours old).

## 4. Recommendations for Improvement

### 1. Smart Caching
Implement explicit cache invalidation for the current year.
```python
if year == current_year:
    # Check file modification time
    if file_age > 24_hours:
        fetch_new()
```

### 2. User-Agent Rotation & Proxies
To bypass the 1.5s rate limit, we could distribute requests across proxies. However, for personal use, the current speed is acceptable and reliable.

### 3. Database Persistence
Move from JSON files to SQLite (`portfolio.db` or dedicated `market_data.db`).
*   **Pros**: Queryable, better for partial updates (append today's price).
*   **Cons**: Higher complexity than simple JSON dump.

### 4. Backup Source
Add Yahoo Finance (`yfinance`) as a fallback if TWSE `MI_INDEX` fails or changes format.
