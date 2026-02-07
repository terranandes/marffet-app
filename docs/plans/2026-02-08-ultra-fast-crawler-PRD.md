# PRD: Ultra-Fast Market Data Crawler

> **For Ralph Loop:** This PRD is formatted for autonomous iteration. Each task is self-contained.

## Overview
Optimize the market data crawler for maximum speed using batch downloads, asyncio, and concurrent processing.

## Problem
Current `crawl_official.py` takes 30-60 minutes for a full cold run (1,959 stocks × 20+ years), processing one stock at a time.

## Goal
Create the fastest possible crawler using yfinance with parallel batch processing - target < 15 minutes.

## Data Sources

| Data | Source | Method |
|------|--------|--------|
| TWSE Stock List | `isin.twse.com.tw` | O(1) parallel fetch |
| TPEx Stock List | `tpex.org.tw` | O(1) parallel fetch |
| All Prices | yfinance `auto_adjust=False` | Mega-batch download |
| All Dividends | yfinance `Dividends` column | Included in batch |

---

## Task 1: Create Base Crawler with Fast List Fetching
Create `tests/ops_scripts/crawl_fast.py` with async functions to fetch TWSE and TPEx stock lists in parallel using httpx and asyncio.

**Acceptance:**
- `fetch_stock_universe()` returns (twse_list, tpex_list)
- Both lists fetched concurrently via `asyncio.gather()`
- TWSE: ~1080 codes, TPEx: ~879 codes

---

## Task 2: Implement Massive Batch Download
Add `download_all_prices()` function that uses yfinance's batch download with ThreadPoolExecutor for parallel processing.

**Acceptance:**
- Batch size: 200 tickers per batch
- 4 concurrent workers via ThreadPoolExecutor
- Uses `yf.download()` with `auto_adjust=False`
- Handles both `.TW` and `.TWO` suffixes

---

## Task 3: Process Data into Cache Format
Add `process_to_cache()` function that converts yfinance DataFrame into MarketCache JSON format with yearly summaries and daily OHLCV.

**Acceptance:**
- Outputs to `data/raw/Market_{Year}_Prices.json`
- Each stock has: `id`, `summary` (start/end/high/low/volume), `daily` (array of OHLCV)
- Handles NaN values gracefully

---

## Task 4: Wire Everything in Main Function
Create `main()` async function that orchestrates: fetch universe → download all → process to cache.

**Acceptance:**
- Complete end-to-end run without manual intervention
- Logs progress and timing
- Handles errors gracefully

---

## Task 5: Verify Cache Integrity
Run verification to confirm data correctness.

**Acceptance:**
- TSMC (2330) 2006 Open price: ~59 (unadjusted)
- Each year has 1500+ stocks
- No empty files

---

## Success Metrics
- **Time**: < 15 minutes for full 2000-2026 crawl
- **Correctness**: TSMC 2006 Open = ~59 (unadjusted, not ~7 adjusted)
- **Coverage**: 1,500+ stocks per year

## Out of Scope
- Real-time streaming data
- Database storage (JSON-only per existing policy)
- Direct TWSE/TPEx API for prices (yfinance is simpler)
