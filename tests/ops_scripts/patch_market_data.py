import asyncio
import json
import logging
import yfinance as yf
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import requests
import time
import math

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger("PatchData")

def _is_valid_number(value) -> bool:
    if value is None:
        return False
    if isinstance(value, float):
        return not (math.isnan(value) or math.isinf(value))
    return True

# Re-use universe fetch (simplified)
async def fetch_universe() -> Dict[str, str]:
    import httpx
    import re
    universe = {}
    
    async def fetch(mode, suffix):
        url = f"https://isin.twse.com.tw/isin/C_public.jsp?strMode={mode}"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, timeout=30)
                text = resp.content.decode('big5', errors='ignore')
                matches = re.findall(r'>([A-Z0-9]{4})[ \u3000]+([^<]+)</td>', text)
                for code, name in matches:
                    universe[code] = f"{code}{suffix}"
            except Exception as e:
                logger.error(f"Fetch mode {mode} failed: {e}")

    await fetch(2, ".TW")
    await fetch(4, ".TWO")
    return universe

import argparse

def patch_year(year: int, universe_map: Dict[str, str]):
    file_path = Path(f"data/raw/Market_{year}_Prices.json")
    
    if not file_path.exists():
        logger.warning(f"File {file_path} not found! Skipping {year}...")
        return

    # 1. Load Existing Data
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    logger.info(f"📂 [{year}] Loaded {len(data)} stocks from {file_path}")
    
    # 2. Identify Missing
    existing_codes = set(data.keys())
    missing_codes = [c for c in universe_map if c not in existing_codes]
    
    # Fail-safe: Ensure 2330 is in missing list if not in data
    critical_stocks = ['2330', '1101', '1102']
    for cs in critical_stocks:
        if cs not in existing_codes and cs not in missing_codes:
            missing_codes.append(cs)
            # Add to universe map manually if fetch failed
            if cs not in universe_map:
                 universe_map[cs] = f"{cs}.TW" # Assume TWSE
                 logger.warning(f"⚠️  Force added {cs} to patch list (Universe fetch might have failed)")
    
    logger.info(f"⚠️  [{year}] Missing: {len(missing_codes)} tickers")
    if not missing_codes:
        logger.info(f"🎉 [{year}] No missing tickers!")
        return

    # 3. Patch Missing
    success_count = 0
    
    logger.info(f"🩹 [{year}] Patching {len(missing_codes)} tickers (1.5s delay)...")
    
    for i, code in enumerate(missing_codes):
        ticker = universe_map[code]
        try:
            # logger.info(f"   [{i+1}/{len(missing_codes)}] Patching {ticker}...")
            
            # Go SLOW.
            df = yf.download(ticker, start=f"{year}-01-01", end=f"{year}-12-31", 
                             progress=False, auto_adjust=False, threads=False)
            
            if df.empty:
                # logger.warning(f"      ❌ Empty DataFrame for {ticker}")
                time.sleep(0.5)
                continue

            # Process to JSON format (same as crawl_fast.py)
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
            
            daily_data = []
            for idx, row in df.iterrows():
                 # Handle MultiIndex
                try:
                    o = row['Open'].iloc[0] if isinstance(row['Open'], pd.Series) else row['Open']
                    h = row['High'].iloc[0] if isinstance(row['High'], pd.Series) else row['High']
                    l = row['Low'].iloc[0] if isinstance(row['Low'], pd.Series) else row['Low']
                    c = row['Close'].iloc[0] if isinstance(row['Close'], pd.Series) else row['Close']
                    v = row['Volume'].iloc[0] if isinstance(row['Volume'], pd.Series) else row['Volume']
                except:
                     o, h, l, c, v = row['Open'], row['High'], row['Low'], row['Close'], row['Volume']

                # Relaxed validation: Allow 0 volume, but require prices
                if not all(_is_valid_number(x) for x in [o, h, l, c]):
                    continue
                
                daily_data.append({
                    "d": idx.strftime("%Y-%m-%d"),
                    "o": float(o), "h": float(h), "l": float(l), "c": float(c), "v": int(v) if _is_valid_number(v) else 0
                })
            
            if daily_data:
                data[code] = {"daily": daily_data}
                success_count += 1
                logger.info(f"      ✅ [{year}] Saved {ticker} ({len(daily_data)} rows)")
            else:
                 pass
                 # logger.warning(f"      ⚠️  No valid daily rows")

            # Save periodically (every 10)
            if success_count > 0 and success_count % 10 == 0:
                 with open(file_path, 'w') as f:
                     json.dump(data, f)
                 logger.info(f"      💾 [{year}] Checkpoint saved.")
                 
            time.sleep(1.5) # generous delay

        except Exception as e:
            logger.error(f"      💥 Error: {e}")
            time.sleep(5.0) # Long pause on error

    # Final Save
    with open(file_path, 'w') as f:
        json.dump(data, f)
    
    logger.info(f"✨ [{year}] Patch Complete! Added {success_count} tickers. Total: {len(data)}")

def main():
    parser = argparse.ArgumentParser(description="Patch missing market data")
    parser.add_argument("--start-year", type=int, default=2024, help="Start year")
    parser.add_argument("--end-year", type=int, default=2024, help="End year")
    args = parser.parse_args()

    # Get Universe ONCE
    universe_map = asyncio.run(fetch_universe())
    logger.info(f"🌌 Universe size: {len(universe_map)}")

    for year in range(args.start_year, args.end_year + 1):
        patch_year(year, universe_map)

if __name__ == "__main__":
    main()
