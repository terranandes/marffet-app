# Ultra-Fast yFinance Crawler Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create the fastest possible market data crawler using yfinance with batch downloads, asyncio, and concurrent processing.

**Architecture:** 
- Stock Lists: O(1) fetch from ISIN (TWSE) and TPEx APIs
- All Price/Dividend Data: yfinance with `auto_adjust=False`
- Concurrency: asyncio + ThreadPoolExecutor for parallel batches

**Tech Stack:** Python, yfinance, asyncio, httpx, aiofiles

---

## Data Source Mapping (User Approved)

| Data | Source | Method |
|------|--------|--------|
| TWSE Stock List | `isin.twse.com.tw` | O(1) fetch |
| TPEx Stock List | `tpex.org.tw/stk_quote` | O(1) fetch |
| Daily Prices (ALL) | yfinance `.TW`/`.TWO` | Batch download |
| Dividends (ALL) | yfinance `Dividends` column | Batch download |
| Names | yfinance `info.shortName` | Included in batch |

---

## Task 1: Optimize Stock List Fetching

**Files:**
- Create: `tests/ops_scripts/crawl_fast.py`

**Step 1: Create base crawler with fast list fetching**

```python
# tests/ops_scripts/crawl_fast.py
import asyncio
import httpx
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def fetch_stock_universe() -> tuple[list, list]:
    """Fetch TWSE + TPEx stock codes in parallel. O(1) fetch."""
    async with httpx.AsyncClient(timeout=30) as client:
        twse_task = fetch_twse_list(client)
        tpex_task = fetch_tpex_list(client)
        twse, tpex = await asyncio.gather(twse_task, tpex_task)
    logging.info(f"Universe: TWSE={len(twse)}, TPEx={len(tpex)}")
    return twse, tpex

async def fetch_twse_list(client) -> list:
    """Fetch TWSE listed stocks from ISIN registry."""
    url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
    resp = await client.get(url)
    text = resp.content.decode('big5', errors='ignore')
    matches = re.findall(r'>([0-9]{4})[\s\u3000]+([^<]+)</td>', text)
    return [m[0] for m in matches]

async def fetch_tpex_list(client) -> list:
    """Fetch TPEx OTC stocks."""
    url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
    params = {"l": "zh-tw", "o": "json"}
    headers = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}
    resp = await client.get(url, params=params, headers=headers)
    data = resp.json()
    codes = []
    for row in data.get('aaData', []):
        if row and len(row[0]) == 4 and row[0].isdigit():
            codes.append(row[0])
    return codes
```

**Step 2: Test list fetching**

Run: `uv run python -c "import asyncio; from tests.ops_scripts.crawl_fast import fetch_stock_universe; print(asyncio.run(fetch_stock_universe()))"`

Expected: `Universe: TWSE=1080, TPEx=879` (approximate)

---

## Task 2: Implement Massive Batch Download

**Files:**
- Modify: `tests/ops_scripts/crawl_fast.py`

**Step 1: Add concurrent batch download function**

```python
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

async def download_all_prices(twse: list, tpex: list, start: str = "2000-01-01", end: str = "2026-12-31") -> pd.DataFrame:
    """Download ALL prices in massive parallel batches."""
    # Build ticker lists
    twse_tickers = [f"{c}.TW" for c in twse]
    tpex_tickers = [f"{c}.TWO" for c in tpex]
    all_tickers = twse_tickers + tpex_tickers
    
    logging.info(f"Downloading {len(all_tickers)} tickers ({start} to {end})...")
    
    # Split into mega-batches for parallel processing
    batch_size = 200  # yfinance handles this well
    batches = [all_tickers[i:i+batch_size] for i in range(0, len(all_tickers), batch_size)]
    
    # Download batches in parallel using ThreadPoolExecutor
    def download_batch(batch):
        try:
            return yf.download(batch, start=start, end=end, auto_adjust=False, 
                             progress=False, threads=True, group_by='ticker')
        except Exception as e:
            logging.error(f"Batch error: {e}")
            return pd.DataFrame()
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [loop.run_in_executor(executor, download_batch, b) for b in batches]
        results = await asyncio.gather(*futures)
    
    # Merge all results
    all_data = pd.concat([r for r in results if not r.empty], axis=1)
    logging.info(f"Downloaded {len(all_data.columns) // 6} tickers with data")
    return all_data
```

**Step 2: Test batch download with small sample**

```python
# Add to crawl_fast.py
async def test_batch_download():
    """Test with 10 stocks each."""
    twse = ['2330', '2317', '2454', '2308', '2382', '1301', '2412', '2881', '2891', '2886']
    tpex = ['6488', '6547', '3105', '5274', '4966', '6669', '3293', '8069', '6472', '5269']
    df = await download_all_prices(twse, tpex, start="2024-01-01", end="2024-12-31")
    print(f"Sample download: {df.shape}")
    return df

if __name__ == "__main__":
    asyncio.run(test_batch_download())
```

Run: `uv run python tests/ops_scripts/crawl_fast.py`

Expected: `Sample download: (250, 120)` (20 tickers × 6 columns ≈ 120)

---

## Task 3: Process Data into Cache Format

**Files:**
- Modify: `tests/ops_scripts/crawl_fast.py`

**Step 1: Add data processing function**

```python
import json

def process_to_cache(df: pd.DataFrame, data_dir: Path = Path("data/raw")) -> dict:
    """Process yfinance DataFrame into MarketCache JSON format."""
    data_dir.mkdir(parents=True, exist_ok=True)
    
    results_by_year = {}
    
    # Get unique tickers from columns
    if isinstance(df.columns, pd.MultiIndex):
        tickers = df.columns.get_level_values(0).unique()
    else:
        return {}
    
    for ticker in tickers:
        try:
            ticker_df = df[ticker].dropna(how='all')
            if ticker_df.empty:
                continue
            
            stock_id = ticker.replace('.TW', '').replace('.TWO', '')
            ticker_df.index = pd.to_datetime(ticker_df.index)
            
            for year in ticker_df.index.year.unique():
                year_data = ticker_df[ticker_df.index.year == year]
                if year_data.empty:
                    continue
                
                if year not in results_by_year:
                    results_by_year[year] = {}
                
                first = year_data.iloc[0]
                last = year_data.iloc[-1]
                
                # Build daily list
                daily = []
                for ts, row in year_data.iterrows():
                    daily.append({
                        "d": ts.strftime('%Y-%m-%d'),
                        "o": round(float(row.get('Open', 0)), 2),
                        "h": round(float(row.get('High', 0)), 2),
                        "l": round(float(row.get('Low', 0)), 2),
                        "c": round(float(row.get('Close', 0)), 2),
                        "v": int(row.get('Volume', 0))
                    })
                
                results_by_year[int(year)][stock_id] = {
                    "id": stock_id,
                    "summary": {
                        "start": round(float(first.get('Open', 0)), 2),
                        "end": round(float(last.get('Close', 0)), 2),
                        "high": round(float(year_data['High'].max()), 2),
                        "low": round(float(year_data['Low'].min()), 2),
                        "volume": int(year_data['Volume'].sum())
                    },
                    "daily": daily
                }
        except Exception as e:
            logging.warning(f"Error processing {ticker}: {e}")
    
    # Save to files
    for year, data in results_by_year.items():
        fpath = data_dir / f"Market_{year}_Prices.json"
        with open(fpath, 'w') as f:
            json.dump(data, f, separators=(',', ':'))
        logging.info(f"Saved {fpath.name}: {len(data)} stocks")
    
    return results_by_year
```

---

## Task 4: Full Crawler Main Function

**Files:**
- Modify: `tests/ops_scripts/crawl_fast.py`

**Step 1: Add main function**

```python
import time

async def main():
    """Ultra-fast full market crawl."""
    start_time = time.time()
    
    # Step 1: Fetch universe (parallel)
    twse, tpex = await fetch_stock_universe()
    
    # Step 2: Download ALL prices (mega-batch parallel)
    df = await download_all_prices(twse, tpex, start="2000-01-01", end="2026-12-31")
    
    # Step 3: Process and save
    data_dir = Path("/home/terwu01/github/martian/data/raw")
    results = process_to_cache(df, data_dir)
    
    elapsed = time.time() - start_time
    total_stocks = sum(len(v) for v in results.values())
    logging.info(f"COMPLETE: {total_stocks} stock-years in {elapsed:.1f}s ({elapsed/60:.1f} min)")

if __name__ == "__main__":
    asyncio.run(main())
```

**Step 2: Run full crawler**

Run: `uv run python tests/ops_scripts/crawl_fast.py`

Expected: Complete in 5-15 minutes (vs 30+ min for sequential)

---

## Task 5: Verify Cache Integrity

**Step 1: Check TSMC 2006 price**

Run: `uv run python -c "import json; d=json.load(open('data/raw/Market_2006_Prices.json')); print('TSMC 2006:', d.get('2330', {}).get('summary', {}))"`

Expected: `start: ~59` (unadjusted)

**Step 2: Check stock count per year**

Run: `uv run python -c "import json; import os; [print(f, len(json.load(open(f'data/raw/{f}')))) for f in sorted(os.listdir('data/raw')) if f.startswith('Market_')]"`

Expected: 1500+ stocks per year

---

## Summary

| Metric | Before (Sequential) | After (Batch+Parallel) |
|--------|---------------------|------------------------|
| Time | 30-60 min | 5-15 min |
| API Calls | 1959 × 1 | 10 batches × 4 workers |
| Concurrency | Single thread | 4 ThreadPool + asyncio |

**Commit after completion:**
```bash
git add tests/ops_scripts/crawl_fast.py
git commit -m "feat: ultra-fast parallel crawler with batch yfinance"
```
