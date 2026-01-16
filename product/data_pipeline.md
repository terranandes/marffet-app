# Data Pipeline Documentation

## 1. Data Sources & Target Data

| Market | Data Type | Source | URL / API | Granularity | Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TWSE** (Listed) | Market Prices (Start/End) | Official TWSE Website | `www.twse.com.tw` (MI_INDEX) | Daily (Sampled at Jan/Dec) | Calculating Annual ROI |
| **TWSE** | Dividends | Official TWSE Website | `TWT49U` report | Annual | ROI Calculation (Yield) |
| **TPEx** (OTC) | Market Prices | Yahoo Finance | `yfinance` | Daily (Full History) | ROI Calculation |
| **TPEx** | Dividends | Official TPEx Website | `web.tpex.org.tw` | Annual | ROI Calculation |

## 2. Concurrency & Parallelism

The pipeline uses Python's `asyncio` for orchestration and `httpx`/`yfinance` for fetching.

### Architecture
1.  **Orchestration (`MarsStrategy.analyze_stock_batch`)**:
    *   **Level 1 Parallelism**: Fetches Dividend Data and Market Prices concurrently (`asyncio.gather`).
    *   **Level 2 Parallelism (TWSE)**: Fetches multiple *years* in parallel (Semaphore: 4).
    *   **Level 2 Parallelism (TPEx)**: Fetches multiple *years* (or full history) in parallel batches.

### Implementation Details

#### TWSE Crawler (`TWSECrawler`)
*   **Concurrency**: `asyncio.Semaphore(4)`
*   **Strategy**: "Sparse Sampling". Instead of downloading 365 days of data, it intelligently queries only the first trading week of January and the last week of December to get Start/End prices.
*   **Rate Limits**: Strictly controlled to prevent IP bans from TWSE.

#### TPEx Crawler (`TPEXCrawler`)
*   **Concurrency**: Batched `asyncio` calls.
*   **Strategy**: "Bulk Download". Uses `yfinance` to download full daily history for batches of 30 tickers at a time.
*   **Efficiency**: Highly efficient as it delegates bandwidth management to the Yahoo Finance API client.

## 3. IPO Strategy (Initial Investment)

### The Challenge
For the Mars Strategy, the "Start Price" is typically the price on the first trading day of the year (Jan 2nd). However, for stocks that **IPO mid-year**, the "Start Price" should be the **First Trading Day (IPO Date)** price.

### Implementations

#### Legacy (Slow - Deprecated)
*   **Logic**: If Jan 2nd price is missing (0.0), scan *every month* of the year by fetching the "Monthly Report" (STOCK_DAY) until a valid price is found.
*   **Cost**: worst-case 12 HTTP requests per IPO stock.
*   **Impact**: drastically slows down "Cold Runs" (cache misses), adding minutes to the process.

#### Current (Fast - Cold Run Optimized)
*   **Logic**: Only checks Jan 2-8. If missing, the stock is marked as "N/A" for that year's ROI.
*   **Cost**: 0 extra requests.
*   **Impact**: Misses IPO opportunities in their listing year, but ensures < 1 minute rebuild time.

#### Proposed (Fast & Accurate)
*   **Logic**: "Listing Date Lookup".
    1.  Fetch a master "Company Basic Info" list (one-time fetch) to get the specific **Listing Date** for all stocks.
    2.  If a stock is missing a Jan price, check its Listing Date.
    3.  If Listing Date is within the current year, make **one single targeted request** to the Daily Quotes (MI_INDEX) API for that specific date.
*   **Cost**: ~1 extra request per IPO stock (negligible).
*   **Impact**: Captures IPO ROI accurately without the performance penalty of the Legacy method.
