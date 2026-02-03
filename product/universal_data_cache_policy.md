# Universal Data & Cache Policy

**Date**: 2026-02-03
**Status**: Active / Enforced
**Scope**: All Market Data Access (Prices, Volumes, History)

## 1. Core Philosophy
> **"One Crawler, One Lake, Instant Access."**

We have moved away from fragmented data sources (Excel, disparate APIs) to a **Universal Clean Room Architecture**.

---

## 2. Ingestion Policy (The "Clean Room")
-   **Sole Source**: `scripts/crawl_official.py`
    -   **Source**: Official TWSE ISIN Registry (`isin.twse.com.tw`).
    -   **Price Source**: `yfinance(auto_adjust=False)` (Verified against physical dividends).
    -   **Frequency**: Once per day (at night).
-   **Granularity**: **Daily OHLCV** (Nested Schema V2).
    -   Stores both *Yearly Summary* (for fast simulation) and *Daily Records* (for charts).

---

## 3. Storage Policy (The "Data Lake")
-   **Format**: JSON Shards by Year.
-   **Location**: `data/raw/Market_{Year}_Prices.json`
-   **Schema (V2)**:
    ```json
    "2330": {
        "id": "2330",
        "summary": { "start": 60, "end": 66, "high": 67, ... },
        "daily": [
            { "d": "2006-01-02", "o": 59.1, "c": 60.0, ... },
            ...
        ]
    }
    ```
-   **Constraint**: No other database (Postgres, SQLite) is used for Market Data in Phase 2/3.
    -   *Logic*: The entire 20-year dataset is < 300MB.

---

## 4. Access Policy (The "MarketCache")
-   **Mechanism**: **In-Memory Singleton** (`app/services/market_cache.py`).
-   **Behavior**:
    -   On App Startup: Loads ALL 21 JSON files (2006-2026) into RAM.
    -   Load Time: ~0.2s.
    -   Read Time: **0.00s (Instant)**.
-   **Usage Rule**:
    -   All features (**Backtest**, **Trend Codes**, **Race Charts**, **Analysis**) MUST use `MarketCache`.
    -   Scanning JSON files from disk inside an API endpoint is **STRICTLY PROHIBITED**.

## 5. Benefits
1.  **Consistency**: Before, "Trend" and "Backtest" might show different data if they read different files. Now, they share the exact same RAM object.
2.  **Performance**: Solves the "20 file open" latency.
3.  **Simplicity**: Deployment is just `git pull`. No DB migration required.

---

## 6. Migration Guide
If adding a new feature that needs price data:
```python
# DO NOT read files.
# DO:
from app.services.market_cache import MarketCache
db = MarketCache.get_prices_db()
data = db[2020]['2330']
```
