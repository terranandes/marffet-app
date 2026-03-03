# DuckDB Architecture (v3.0)

**Date**: 2026-02-14
**Status**: DEPLOYED
**Primary Storage**: `data/market.duckdb`

## 1. Overview
As of v3.0, the Marffet system has transitioned from a JSON-based memory cache to a **columnar DuckDB DataLake**. This move was driven by the need to:
- Reduce RAM usage on constrained environments (Zeabur).
- Support large-scale, daily-level financial simulations (Mars Strategy).
- Achieve O(1) cold-start performance for the dashboard.

## 2. Component Diagram
```mermaid
graph TD
    subgraph "External Sources"
        TWSE_MI["TWSE MI_INDEX (Nominal Prices)"]
        YF["yfinance (TPEx Fallback)"]
        TWSE["TWSE/TPEx Dividend APIs"]
    end

    subgraph "Data Acquisition"
        Backfill["Backfill Service (app/services/market_data_service.py)"]
    end

    subgraph "Storage Layer"
        DuckDB[("DuckDB: market.duckdb")]
        MemoryCache["Latest Price Cache (In-Memory ~175KB)"]
    end

    subgraph "Consumer Layer"
        Provider["MarketDataProvider (app/services/market_data_provider.py)"]
        Mars["Mars Strategy Engine"]
        Race["Bar Chart Race Engine"]
        API["FastAPI Endpoints"]
    end

    TWSE_MI --> Backfill
    YF --> Backfill
    TWSE --> Backfill
    Backfill --> DuckDB
    DuckDB --> Provider
    Provider --> MemoryCache
    Provider --> Mars
    Provider --> Race
    Provider --> API
```

## 3. Schema Design

### 3.1 `daily_prices`
Optimized for time-series range queries. Columns are compressed using DuckDB's default encodings.
- `stock_id`: VARCHAR (TICKER)
- `date`: DATE
- `open`, `high`, `low`, `close`, `change`: DOUBLE
- `volume`: BIGINT
- `market`: VARCHAR (TWSE/TPEx)

### 3.2 `dividends`
- `stock_id`: VARCHAR
- `year`: INTEGER
- `cash_dividend`: DOUBLE
- `stock_dividend`: DOUBLE

### 3.3 `stocks`
- `stock_id`: VARCHAR (PK)
- `name`: VARCHAR
- `market_type`: VARCHAR
- `industry`: VARCHAR

## 4. Performance Benchmarks

| Metric | Legacy (JSON) | New (DuckDB) | Improvement |
|--------|---------------|--------------|-------------|
| RAM Usage (Idle) | ~2.7 GB | ~50 MB | **98% Reduction** |
| Cold Start Time | ~120s | < 2s | **60x Faster** |
| ROI Simulation (Top 200) | ~36s | ~1.5s | **24x Faster** |
| Storage Format | Uncompressed JSON | Compressed Columnar | ~4x Savings |

## 5. Maintenance & Operations
- **Standard**: All history is stored in **NOMINAL** prices. Adjustments are performed at runtime by the `SplitDetector`.
- **Integrity Checks**: Use `scripts/ops/verify_integrity.py` to ensure daily row continuity.
- **Statistics**: `/api/admin/market-data/stats` provides live monitoring of row counts and DB size.

## 6. Why is the Mars Tab So Fast? (Multi-User Caching & Cold Starts)
When deploying to serverless/containerized environments like Zeabur, the Mars Strategy Tab exhibits sub-second load times even from a cold start. This is achieved through three key architectural pillars:
1. **Singleton Memory Loading:** Upon the very first request (Cold Start) by *any* user, the `MarketDataProvider` singleton queries DuckDB and caches the most heavily accessed datasets (price histories and dividends) directly into RAM (using Pandas DataFrames).
2. **Shared Multi-User Access:** Because the `MarketDataProvider` operates as a global singleton across the FastAPI worker processes, once User A loads the data, the DuckDB disk step is entirely bypassed for User B, C, and D. They inherit the O(1) in-memory lookup speeds instantly.
3. **Vectorized Mathematics:** The inner `ROICalculator` uses NumPy vectorization instead of slow Python `for` loops. The compounding and share-split adjustments over 24 years of daily data are calculated simultaneously in mathematical blocks.
