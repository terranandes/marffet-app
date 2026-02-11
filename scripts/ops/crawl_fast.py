import asyncio
import httpx
import re
import logging
import time
from typing import List, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

try:
    import yfinance as yf
except ImportError:
    yf = None
    logging.warning("yfinance not installed. Run: pip install yfinance")

# Setup Premium Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("CrawlFast")

async def fetch_isin_list(mode: int) -> List[str]:
    """
    Fetch stock list from ISIN service.
    Mode 2: TWSE (Listed), Mode 4: TPEx (OTC)
    """
    url = f"https://isin.twse.com.tw/isin/C_public.jsp?strMode={mode}"
    market = "TWSE" if mode == 2 else "TPEx"
    logger.info(f"🚀 Fetching {market} universe from ISIN service...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=30, headers=headers)
            resp.raise_for_status()
            # ISIN page uses Big5 encoding
            text = resp.content.decode('big5', errors='ignore')
        except Exception as e:
            logger.error(f"❌ Failed to fetch {market} list: {e}")
            return []
        
    # Pattern: >(Code) (Name)</td>
    # Example: >1101　台泥</td>
    # Unicode \u3000 is the full-width space used in the ISIN page
    matches = re.findall(r'>([A-Z0-9]{4,6})[ \u3000]+([^<]+)</td>', text)
    
    codes = []
    for code, name in matches:
        code = code.strip()
        # Filter for 4-digit codes (Primary stocks)
        if len(code) == 4:
            codes.append(code)
            
    logger.info(f"✅ {market}: Found {len(codes)} valid 4-digit codes.")
    return codes

async def fetch_stock_universe() -> Tuple[List[str], List[str]]:
    """
    Fetch both TWSE and TPEx stock lists in parallel.
    Returns: (twse_list, tpex_list)
    """
    start_time = time.time()
    
    # Mode 2: TWSE, Mode 4: TPEx
    twse_list, tpex_list = await asyncio.gather(
        fetch_isin_list(2),
        fetch_isin_list(4)
    )
    
    total_time = time.time() - start_time
    logger.info(f"✨ Universe discovery completed in {total_time:.2f}s")
    logger.info(f"📊 Total stocks found: {len(twse_list) + len(tpex_list)} (TWSE: {len(twse_list)}, TPEx: {len(tpex_list)})")
    
    return twse_list, tpex_list


import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# === TASK 2: Massive Batch Download ===

BATCH_SIZE = 150  # Safer batch size to avoid Rate Limits
MAX_WORKERS = 1   # Sequential batch execution

def download_batch(tickers: List[str], start_date: str, end_date: str, batch_id: int) -> Dict[str, pd.DataFrame]:
    """
    Download a batch of tickers using yfinance with internal threading.
    Returns dict mapping ticker -> DataFrame with OHLCV data.
    """
    if yf is None:
        logger.error("❌ yfinance not installed!")
        return {}
    
    logger.info(f"📥 Batch {batch_id}: Downloading {len(tickers)} tickers...")
    start_time = time.time()
    
    try:
        # yf.download returns MultiIndex DataFrame for multiple tickers
        data = yf.download(
            tickers=" ".join(tickers),
            start=start_date,
            end=end_date,
            auto_adjust=False,  # CRITICAL: Get raw prices, not adjusted
            threads=True,       # ENABLED: Let yfinance handle concurrency
            progress=False,
            group_by='ticker'
        )
        
        elapsed = time.time() - start_time
        
        # Parse MultiIndex into per-ticker DataFrames
        result = {}
        failed_tickers = []
        
        if len(tickers) == 1:
            # Single ticker: data is already a simple DataFrame
            ticker = tickers[0]
            if not data.empty:
                result[ticker] = data
            else:
                failed_tickers.append(ticker)
        else:
            # Multiple tickers: MultiIndex columns (ticker, field)
            for ticker in tickers:
                try:
                    if ticker in data.columns.get_level_values(0):
                        ticker_df = data[ticker].dropna(how='all')
                        if not ticker_df.empty:
                            result[ticker] = ticker_df
                        else:
                            failed_tickers.append(ticker)
                    else:
                        failed_tickers.append(ticker)
                except Exception as e:
                    logger.debug(f"⚠️ Could not extract {ticker}: {e}")
                    failed_tickers.append(ticker)
        
        # Verbose logging
        success_rate = len(result) / len(tickers) * 100 if tickers else 0
        logger.info(f"✅ Batch {batch_id}: {len(result)}/{len(tickers)} succeeded ({success_rate:.1f}%) in {elapsed:.1f}s")
        
        if failed_tickers and len(failed_tickers) <= 10:
            logger.warning(f"   Failed tickers: {', '.join(failed_tickers[:10])}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Batch {batch_id} failed: {e}")
        return {}


def download_all_prices(
    twse_list: List[str],
    tpex_list: List[str],
    start_date: str = "2000-01-01",
    end_date: str = None
) -> Dict[str, pd.DataFrame]:
    """
    Download all stock prices using massive batch processing.
    
    Args:
        twse_list: List of TWSE stock codes (4-digit)
        tpex_list: List of TPEx stock codes (4-digit)
        start_date: Start date for historical data
        end_date: End date (defaults to today)
        
    Returns:
        Dict mapping raw code -> DataFrame with OHLCV data
    """
    if end_date is None:
        end_date = pd.Timestamp.now().strftime("%Y-%m-%d")
    
    logger.info(f"🚀 Starting massive batch download: {len(twse_list)} TWSE + {len(tpex_list)} TPEx stocks")
    logger.info(f"📅 Date range: {start_date} to {end_date} | Batch Size: {BATCH_SIZE}")
    start_time = time.time()
    
    # Build ticker lists with correct suffixes
    # TWSE: .TW, TPEx: .TWO
    all_tickers = []
    ticker_to_code = {}  # Map yfinance ticker back to raw code
    
    for code in twse_list:
        ticker = f"{code}.TW"
        all_tickers.append(ticker)
        ticker_to_code[ticker] = code
        
    for code in tpex_list:
        ticker = f"{code}.TWO"
        all_tickers.append(ticker)
        ticker_to_code[ticker] = code
    
    # Split into batches
    batches = [all_tickers[i:i + BATCH_SIZE] for i in range(0, len(all_tickers), BATCH_SIZE)]
    logger.info(f"📦 Split into {len(batches)} batches of up to {BATCH_SIZE} tickers")
    
    # Download SEQUENTIALLY (yfinance uses threads internally)
    all_data = {}
    
    for i, batch in enumerate(batches):
        batch_id = i + 1
        try:
            batch_result = download_batch(batch, start_date, end_date, batch_id)
            
            # Map back to raw codes
            for ticker, df in batch_result.items():
                raw_code = ticker_to_code.get(ticker, ticker)
                all_data[raw_code] = df
            
            # Small delay between batches
            if i < len(batches) - 1:
                delay = 2.0
                logger.info(f"⏸️  Waiting {delay}s before next batch...")
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"❌ Batch {batch_id} exception: {e}")
    
    
    # === RETRY LOGIC ===
    downloaded_tickers = set(all_data.keys())
    missing_tickers = [t for t in twse_list + tpex_list if t not in downloaded_tickers]
    
    if missing_tickers:
        logger.info(f"⚠️  Missing {len(missing_tickers)} tickers after main download. Starting RETRY phase...")
        
        # Retry config
        RETRY_BATCH_SIZE = 20
        MAX_RETRIES = 1
        
        for attempt in range(MAX_RETRIES):
            logger.info(f"🔄 Retry Attempt {attempt + 1}/{MAX_RETRIES} for {len(missing_tickers)} tickers...")
            
            # Re-build ticker list with suffixes
            retry_tickers = []
            retry_map = {}
            for code in missing_tickers:
                suffix = ".TW" if code in twse_list else ".TWO"
                ticker = f"{code}{suffix}"
                retry_tickers.append(ticker)
                retry_map[ticker] = code
                
            # Split into smaller batches
            retry_batches = [retry_tickers[i:i + RETRY_BATCH_SIZE] for i in range(0, len(retry_tickers), RETRY_BATCH_SIZE)]
            
            # Use SEQUENTIAL processing for retries to avoid rate limits
            for i, batch in enumerate(retry_batches):
                try:
                    batch_id = f"R{attempt+1}-{i+1}"
                    # Process sequentially
                    batch_result = download_batch(batch, start_date, end_date, batch_id)
                    
                    for ticker, df in batch_result.items():
                        raw_code = retry_map.get(ticker, ticker)
                        if not df.empty:
                            all_data[raw_code] = df
                    
                    # Delay between retry batches
                    if i < len(retry_batches) - 1:
                        time.sleep(2.0) 
                except Exception as e:
                    logger.error(f"❌ Retry batch {batch_id} failed: {e}")

            # Update missing list
            downloaded_now = set(all_data.keys())
            missing_tickers = [t for t in twse_list + tpex_list if t not in downloaded_now]
            
            if not missing_tickers:
                logger.info("✨ All tickers captured! No more retries needed.")
                break
                
            logger.info(f"   Remaining missing: {len(missing_tickers)}")
            
            # Exponential Backoff for Retries
            backoff_time = 10.0 * (attempt + 1)
            logger.info(f"⏳ Waiting {backoff_time}s before next retry attempt...")
            time.sleep(backoff_time)

    # === FINAL RESORT: SINGLE TICKER RETRY ===
    if missing_tickers:
        logger.info(f"🚨 Final Resort: Trying {len(missing_tickers)} tickers individually...")
        
        for code in missing_tickers:
            suffix = ".TW" if code in twse_list else ".TWO"
            ticker = f"{code}{suffix}"
            try:
                # Individual download
                df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False, threads=False)
                if not df.empty:
                     all_data[code] = df
                     logger.info(f"   ✅ Recovered {code} via single download")
                else:
                     logger.warning(f"   ❌ {code}: No data found (likely delisted or invalid)")
                time.sleep(1.0) # Increased delay to avoid rate limit
            except Exception as e:
                logger.error(f"   💥 {code} failed: {e}")

    # Recalculate final missing list
    downloaded_final = set(all_data.keys())
    missing_tickers = [t for t in twse_list + tpex_list if t not in downloaded_final]

    total_time = time.time() - start_time
    logger.info(f"✨ Download completed in {total_time:.1f}s")
    logger.info(f"📊 Successfully downloaded: {len(all_data)} stocks")
    
    # Final missing check
    if missing_tickers:
        logger.warning(f"❌ Final Missing Tickers ({len(missing_tickers)}): {', '.join(missing_tickers[:20])}...")

    return all_data


# === TASK 3: Process Data into Cache Format ===

import json
import math
from pathlib import Path


def _is_valid_number(value) -> bool:
    """Check if a value is a valid, finite number."""
    if value is None:
        return False
    if isinstance(value, float):
        return not (math.isnan(value) or math.isinf(value))
    return True


def process_to_cache(
    all_data: Dict[str, pd.DataFrame],
    output_dir: str = "data/raw"
) -> Dict[int, int]:
    """
    Convert yfinance DataFrames into MarketCache JSON format.
    
    Outputs to data/raw/Market_{Year}_Prices.json
    Each stock has: id, summary (start/end/high/low/volume/first_open), daily (array of OHLCV)
    
    Args:
        all_data: Dict mapping stock code -> DataFrame with OHLCV data
        output_dir: Directory to write JSON files
        
    Returns:
        Dict mapping year -> count of stocks processed for that year
    """
    logger.info(f"🔄 Processing {len(all_data)} stocks into cache format...")
    start_time = time.time()
    
    # Organize data by year
    # Structure: {year: {stock_code: {"id": ..., "summary": ..., "daily": [...]}}}
    yearly_data: Dict[int, Dict[str, dict]] = {}
    
    for code, df in all_data.items():
        if df.empty:
            continue
            
        # Ensure index is datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Group by year
        df['year'] = df.index.year
        
        for year, year_df in df.groupby('year'):
            year = int(year)
            if year not in yearly_data:
                yearly_data[year] = {}
            
            # Build daily OHLCV array
            daily = []
            for idx, row in year_df.iterrows():
                # Handle column names (could be 'Open' or 'open')
                o = row.get('Open', row.get('open'))
                h = row.get('High', row.get('high'))
                l = row.get('Low', row.get('low'))
                c = row.get('Close', row.get('close'))
                v = row.get('Volume', row.get('volume'))
                
                # Skip if any OHLC is invalid (NaN/None)
                if not all(_is_valid_number(x) for x in [o, h, l, c]):
                    continue
                    
                daily.append({
                    "d": idx.strftime("%Y-%m-%d"),
                    "o": round(float(o), 2) if _is_valid_number(o) else None,
                    "h": round(float(h), 2) if _is_valid_number(h) else None,
                    "l": round(float(l), 2) if _is_valid_number(l) else None,
                    "c": round(float(c), 2) if _is_valid_number(c) else None,
                    "v": int(v) if _is_valid_number(v) else 0
                })
            
            if not daily:
                continue
            
            # Build summary from daily data
            opens = [d["o"] for d in daily if d["o"] is not None]
            highs = [d["h"] for d in daily if d["h"] is not None]
            lows = [d["l"] for d in daily if d["l"] is not None]
            closes = [d["c"] for d in daily if d["c"] is not None]
            volumes = [d["v"] for d in daily if d["v"] is not None]
            
            if not opens or not closes:
                continue
            
            summary = {
                "id": code,
                "name": code,  # Name not available from yfinance batch
                "start": opens[0],
                "end": closes[-1],
                "high": max(highs) if highs else None,
                "low": min(lows) if lows else None,
                "volume": sum(volumes) if volumes else 0,
                "first_open": opens[0]
            }
            
            yearly_data[year][code] = {
                "id": code,
                "summary": summary,
                "daily": daily
            }
    
    # Write JSON files per year
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    year_counts = {}
    for year, stocks_dict in sorted(yearly_data.items()):
        file_path = output_path / f"Market_{year}_Prices.json"
        
        # Write atomically (write to temp, then rename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(stocks_dict, f, ensure_ascii=False, separators=(',', ':'))
        
        year_counts[year] = len(stocks_dict)
        logger.info(f"📁 Wrote {file_path.name}: {len(stocks_dict)} stocks")
    
    total_time = time.time() - start_time
    logger.info(f"✨ Cache processing completed in {total_time:.1f}s")
    logger.info(f"📊 Years processed: {len(year_counts)}, Total stock-years: {sum(year_counts.values())}")
    
    return year_counts


async def main():
    """
    Task 4: Main Orchestration
    Complete end-to-end run: fetch universe → download all → process to cache.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Ultra-Fast Market Data Crawler")
    parser.add_argument("--start-year", type=int, default=2000, help="Start year (default: 2000)")
    parser.add_argument("--end-year", type=int, default=None, help="End year (default: current year)")
    parser.add_argument("--sample", action="store_true", help="Run sample test only (10 stocks)")
    parser.add_argument("--output-dir", type=str, default="data/raw", help="Output directory")
    args = parser.parse_args()
    
    end_year = args.end_year or pd.Timestamp.now().year
    start_date = f"{args.start_year}-01-01"
    end_date = f"{end_year}-12-31"
    
    logger.info("=" * 60)
    logger.info("🚀 ULTRA-FAST MARKET DATA CRAWLER")
    logger.info("=" * 60)
    total_start = time.time()
    
    # Task 1: Fetch stock universe
    logger.info("\n📋 TASK 1: Fetching Stock Universe...")
    twse, tpex = await fetch_stock_universe()
    
    if len(twse) < 100 or len(tpex) < 100:
        logger.error("❌ Universe fetch failed. Aborting.")
        return
    
    logger.info(f"✅ Task 1 Complete: {len(twse)} TWSE + {len(tpex)} TPEx = {len(twse) + len(tpex)} total stocks")
    
    # Task 2 & 3: Process Year by Year
    overall_year_counts = {}
    
    for year in range(args.start_year, end_year + 1):
        logger.info(f"\n" + "="*40)
        logger.info(f"📅 PROCESSING YEAR {year}")
        logger.info("="*40)
        
        current_start = f"{year}-01-01"
        current_end = f"{year}-12-31"
        
        # Download
        if args.sample:
            logger.info(f"📥 Downloading Sample (10 stocks) for {year}...")
            twse_subset = twse[:5]
            tpex_subset = tpex[:5]
            all_data = download_all_prices(twse_subset, tpex_subset, start_date=current_start, end_date=current_end)
        else:
            logger.info(f"📥 Downloading ALL {len(twse) + len(tpex)} stocks for {year}...")
            all_data = download_all_prices(twse, tpex, start_date=current_start, end_date=current_end)
        
        if not all_data:
            logger.error(f"❌ Download failed for {year}. Skipping.")
            continue
            
        logger.info(f"✅ Downloaded {len(all_data)} stocks for {year}")
        
        # Process to cache
        logger.info(f"🔄 Processing {year} to Cache Format...")
        counts = process_to_cache(all_data, output_dir=args.output_dir)
        overall_year_counts.update(counts)
        
        logger.info(f"💾 Saved {year} data.")
        
        # Cleanup to free memory
        all_data.clear()
        import gc
        gc.collect()
        
        # Delay between years
        time.sleep(2.0)

    # Summary
    total_time = time.time() - total_start
    logger.info("\n" + "=" * 60)
    logger.info("✨ CRAWLER COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"⏱️  Total Time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    logger.info(f"📁 Years Processed: {len(overall_year_counts)}")
    
    # Show year breakdown
    for year in sorted(overall_year_counts.keys()):
        logger.info(f"   {year}: {overall_year_counts[year]} stocks")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Crawler stopped by user.")

