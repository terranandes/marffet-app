# Universal Data Lake (Phase 2) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace JSON-based yearly summaries with a Parquet/DuckDB-backed Daily OHLCV data lake, enabling high-precision simulations across all stocks.

**Architecture:**
- **Storage**: Parquet files per market/year (`data/lake/twse_2026.parquet`).
- **Query Interface**: DuckDB for instant SQL queries.
- **Integration**: Update `MarketCache` to read from Parquet instead of JSON.

**Tech Stack:** Python, Polars, DuckDB, Parquet, httpx/asyncio

---

## Task 1: Setup Parquet Schema & Write Test

**Files:**
- Create: `app/services/data_lake.py`
- Create: `tests/unit/test_data_lake.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_data_lake.py
import pytest
from app.services.data_lake import DataLake

def test_write_and_read_daily_prices():
    lake = DataLake(base_path="./test_data_lake")
    
    sample_data = [
        {"date": "2026-01-02", "stock_id": "2330", "open": 60.0, "high": 62.0, "low": 59.5, "close": 61.0, "volume": 1000000},
        {"date": "2026-01-03", "stock_id": "2330", "open": 61.0, "high": 63.0, "low": 60.0, "close": 62.5, "volume": 1200000},
    ]
    
    lake.write_daily("twse", 2026, sample_data)
    
    result = lake.read_stock("2330", 2026)
    
    assert len(result) == 2
    assert result[0]["close"] == 61.0
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_data_lake.py::test_write_and_read_daily_prices -v
```
Expected: FAIL with "ModuleNotFoundError: No module named 'app.services.data_lake'"

**Step 3: Write minimal implementation**

```python
# app/services/data_lake.py
import polars as pl
from pathlib import Path
from typing import List, Dict, Any

class DataLake:
    """Parquet-based Data Lake for Daily OHLCV Storage."""
    
    def __init__(self, base_path: str = "./data/lake"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_path(self, market: str, year: int) -> Path:
        return self.base_path / f"{market}_{year}.parquet"
    
    def write_daily(self, market: str, year: int, data: List[Dict[str, Any]]) -> None:
        """Write daily OHLCV data to Parquet."""
        df = pl.DataFrame(data)
        df.write_parquet(self._get_path(market, year))
    
    def read_stock(self, stock_id: str, year: int, market: str = "twse") -> List[Dict[str, Any]]:
        """Read daily data for a specific stock."""
        path = self._get_path(market, year)
        if not path.exists():
            return []
        df = pl.read_parquet(path)
        filtered = df.filter(pl.col("stock_id") == stock_id)
        return filtered.to_dicts()
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_data_lake.py::test_write_and_read_daily_prices -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add app/services/data_lake.py tests/unit/test_data_lake.py
git commit -m "feat(data-lake): add parquet-based DataLake class with read/write"
```

---

## Task 2: DuckDB Query Interface

**Files:**
- Modify: `app/services/data_lake.py`
- Modify: `tests/unit/test_data_lake.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_data_lake.py
def test_query_with_duckdb():
    lake = DataLake(base_path="./test_data_lake")
    
    result = lake.query_sql("""
        SELECT stock_id, AVG(close) as avg_close 
        FROM read_parquet('twse_2026.parquet') 
        WHERE stock_id = '2330'
        GROUP BY stock_id
    """)
    
    assert len(result) == 1
    assert result[0]["stock_id"] == "2330"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_data_lake.py::test_query_with_duckdb -v
```
Expected: FAIL with "AttributeError: 'DataLake' object has no attribute 'query_sql'"

**Step 3: Write minimal implementation**

```python
# Add to app/services/data_lake.py
import duckdb

class DataLake:
    # ... existing methods ...
    
    def query_sql(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL query using DuckDB against the data lake."""
        conn = duckdb.connect()
        # Register all parquet files in the base path
        for pq_file in self.base_path.glob("*.parquet"):
            table_name = pq_file.stem  # e.g., "twse_2026"
            conn.execute(f"CREATE VIEW IF NOT EXISTS {table_name} AS SELECT * FROM read_parquet('{pq_file}')")
        
        result = conn.execute(sql).fetchdf()
        return result.to_dict(orient="records")
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_data_lake.py::test_query_with_duckdb -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add app/services/data_lake.py tests/unit/test_data_lake.py
git commit -m "feat(data-lake): add DuckDB SQL query interface"
```

---

## Task 3: Update TWSECrawler to Output Daily Data

**Files:**
- Modify: `app/scrapers/twse_crawler.py` (or equivalent)
- Create: `tests/integration/test_twse_daily_crawl.py`

**Step 1: Write the failing test**

```python
# tests/integration/test_twse_daily_crawl.py
import pytest
from app.scrapers.twse_crawler import TWSECrawler

@pytest.mark.asyncio
async def test_fetch_daily_ohlcv():
    crawler = TWSECrawler()
    
    # Fetch one month of data for a known stock
    data = await crawler.fetch_daily("2330", 2025, 1)  # Jan 2025
    
    assert len(data) >= 15  # ~15-20 trading days
    assert all("open" in d and "close" in d for d in data)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/integration/test_twse_daily_crawl.py -v
```
Expected: FAIL with "AttributeError: 'TWSECrawler' object has no attribute 'fetch_daily'"

**Step 3: Write minimal implementation**

```python
# Add to app/scrapers/twse_crawler.py
async def fetch_daily(self, stock_id: str, year: int, month: int) -> List[Dict]:
    """Fetch daily OHLCV from TWSE MI_INDEX API."""
    url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&stockNo={stock_id}&date={year}{month:02d}01"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
    
    if "data" not in data:
        return []
    
    result = []
    for row in data["data"]:
        # Parse TWSE format: [date, volume, $vol, open, high, low, close, delta, quantity]
        result.append({
            "date": row[0],
            "stock_id": stock_id,
            "open": float(row[3].replace(",", "")),
            "high": float(row[4].replace(",", "")),
            "low": float(row[5].replace(",", "")),
            "close": float(row[6].replace(",", "")),
            "volume": int(row[1].replace(",", ""))
        })
    return result
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/integration/test_twse_daily_crawl.py -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add app/scrapers/twse_crawler.py tests/integration/test_twse_daily_crawl.py
git commit -m "feat(crawler): add daily OHLCV fetching to TWSECrawler"
```

---

## Task 4: Integrate DataLake with MarketCache

**Files:**
- Modify: `app/services/market_cache.py`
- Modify: `tests/unit/test_market_cache.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_market_cache.py
def test_market_cache_uses_data_lake():
    # Assumes data lake has been populated
    from app.services.market_cache import MarketCache
    
    history = MarketCache.get_stock_history_fast("2330")
    
    # Expect daily granularity (many rows per year)
    assert len(history) > 100  # At least 100 trading days across years
```

**Step 2: Implement integration (Update MarketCache to check DataLake first)**

```python
# app/services/market_cache.py
from app.services.data_lake import DataLake

class MarketCache:
    _data_lake = None
    
    @classmethod
    def _get_data_lake(cls):
        if cls._data_lake is None:
            cls._data_lake = DataLake()
        return cls._data_lake
    
    @classmethod
    def get_stock_history_fast(cls, stock_id: str) -> list:
        # Try DataLake first (Daily data)
        lake = cls._get_data_lake()
        all_data = []
        for year in range(2006, 2027):
            all_data.extend(lake.read_stock(stock_id, year))
        
        if all_data:
            return all_data
        
        # Fallback to legacy JSON cache
        return cls._legacy_get_stock_history(stock_id)
```

**Step 3: Run test and commit**

```bash
pytest tests/unit/test_market_cache.py -v
git add app/services/market_cache.py
git commit -m "feat(market-cache): integrate DataLake as primary data source"
```

---

## Task 5: Full Year Crawl & Population Script

**Files:**
- Create: `scripts/populate_data_lake.py`

**Implementation:**

```python
#!/usr/bin/env python3
"""Script to populate the Data Lake with Daily OHLCV for all stocks."""
import asyncio
from app.scrapers.twse_crawler import TWSECrawler
from app.services.data_lake import DataLake

async def main():
    lake = DataLake()
    crawler = TWSECrawler()
    
    stock_ids = ["2330", "2317", "2454"]  # Start with top stocks
    
    for year in range(2020, 2027):
        all_data = []
        for stock_id in stock_ids:
            for month in range(1, 13):
                data = await crawler.fetch_daily(stock_id, year, month)
                all_data.extend(data)
                print(f"Fetched {stock_id} {year}/{month}: {len(data)} rows")
        
        lake.write_daily("twse", year, all_data)
        print(f"Wrote {len(all_data)} rows to twse_{year}.parquet")

if __name__ == "__main__":
    asyncio.run(main())
```

**Run & Commit:**

```bash
python scripts/populate_data_lake.py
git add scripts/populate_data_lake.py
git commit -m "feat(scripts): add data lake population script"
```

---

## Verification Checklist

- [ ] `pytest tests/unit/test_data_lake.py -v` → All PASS
- [ ] `pytest tests/unit/test_market_cache.py -v` → All PASS
- [ ] `python scripts/populate_data_lake.py` → Parquet files created
- [ ] App startup: `./start_app.sh` → MarketCache uses DataLake
- [ ] Mars Strategy Modal → Shows same values as before (regression test)

---

## Dependencies to Install

```bash
uv add polars duckdb
```

