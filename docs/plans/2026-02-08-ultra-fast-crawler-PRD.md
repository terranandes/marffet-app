# PRD: Ultra-Fast Market Data Crawler

## Overview
Optimize the market data crawler for maximum speed using batch downloads, asyncio, and concurrent processing.

## Problem
Current `crawl_official.py` takes 30-60 minutes for a full cold run (1,959 stocks × 20+ years), processing one stock at a time.

## Solution
Replace sequential fetching with parallel batch processing:
- **200 tickers per batch** (instead of 1)
- **4 concurrent workers** (ThreadPoolExecutor)
- **asyncio orchestration** for non-blocking I/O

## Data Sources

| Data | Source |
|------|--------|
| TWSE Stock List | `isin.twse.com.tw` (O(1) fetch) |
| TPEx Stock List | `tpex.org.tw` (O(1) fetch) |
| All Prices | yfinance `auto_adjust=False` |
| All Dividends | yfinance `Dividends` column |

## Success Metrics
- **Time**: < 15 minutes for full crawl (vs 30-60 min)
- **Correctness**: TSMC 2006 Open = ~59 (unadjusted)
- **Coverage**: 1,500+ stocks per year

## Deliverables
1. `tests/ops_scripts/crawl_fast.py` - New optimized crawler
2. Cached JSON files in `data/raw/Market_{Year}_Prices.json`

## Out of Scope
- Real-time streaming data
- Database storage (JSON-only per existing policy)
- Direct TWSE/TPEx API for prices (yfinance is simpler)
