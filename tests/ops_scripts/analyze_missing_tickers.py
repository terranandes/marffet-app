import asyncio
import httpx
import re
import json
import logging
import yfinance as yf
from pathlib import Path
from typing import List, Set

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger("AnalyzeMissing")

# Re-use fetch logic from crawl_fast.py
async def fetch_isin_list(mode: int) -> List[str]:
    url = f"https://isin.twse.com.tw/isin/C_public.jsp?strMode={mode}"
    market = "TWSE" if mode == 2 else "TPEx"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=30, headers=headers)
            text = resp.content.decode('big5', errors='ignore')
            # Regex to capture Code AND Name
            matches = re.findall(r'>([A-Z0-9]{4})[ \u3000]+([^<]+)</td>', text)
            return [(code, name, market) for code, name in matches]
        except Exception as e:
            logger.error(f"Failed to fetch {market}: {e}")
            return []

async def main():
    logger.info("🚀 Starting Missing Ticker Analysis...")
    
    # 1. Fetch Universe
    twse_raw = await fetch_isin_list(2)
    tpex_raw = await fetch_isin_list(4)
    
    universe_map = {} # code -> (name, market, expected_suffix)
    
    for code, name, market in twse_raw:
        universe_map[code] = (name, market, ".TW")
        
    for code, name, market in tpex_raw:
        universe_map[code] = (name, market, ".TWO")
        
    logger.info(f"📊 Universe Size: {len(universe_map)} (TWSE: {len(twse_raw)}, TPEx: {len(tpex_raw)})")
    
    # 2. Load Downloaded Data (2024 sample)
    data_path = Path("data/raw/Market_2024_Prices.json")
    if not data_path.exists():
        logger.error("❌ Market_2024_Prices.json not found! Run crawl first.")
        return
        
    with open(data_path, 'r') as f:
        downloaded_data = json.load(f)
        
    downloaded_codes = set(downloaded_data.keys())
    logger.info(f"💾 Downloaded Size: {len(downloaded_codes)}")
    
    # 3. Identify Missing
    missing_codes = [code for code in universe_map if code not in downloaded_codes]
    logger.info(f"⚠️  Missing: {len(missing_codes)} ({len(missing_codes)/len(universe_map):.1%})")
    
    # 4. Analyze Missing Samples
    if not missing_codes:
        logger.info("🎉 No missing codes!")
        return

    # Categorize missing
    missing_twse = [c for c in missing_codes if universe_map[c][1] == "TWSE"]
    missing_tpex = [c for c in missing_codes if universe_map[c][1] == "TPEx"]
    
    logger.info(f"   Missing TWSE: {len(missing_twse)}")
    logger.info(f"   Missing TPEx: {len(missing_tpex)}")
    
    # Test a sample of 10 missing tickers
    sample_size = 10
    sample = missing_codes[:sample_size]
    
    logger.info(f"\n🔍 Testing {sample_size} missing tickers individually:")
    
    for code in sample:
        name, market, suffix = universe_map[code]
        ticker = f"{code}{suffix}"
        
        logger.info(f"   Checking {ticker} ({name})...")
        
        # Try downloading
        try:
            df = yf.download(ticker, start="2024-01-01", end="2024-12-31", progress=False, auto_adjust=False)
            if not df.empty:
                logger.info(f"      ✅ OK! Data found ({len(df)} rows). Why was it missing?")
            else:
                logger.warning(f"      ❌ Empty DataFrame. (No data)")
                
                # Try Alternative Suffix?
                alt_suffix = ".TWO" if suffix == ".TW" else ".TW"
                alt_ticker = f"{code}{alt_suffix}"
                logger.info(f"      🔄 Trying alternative: {alt_ticker}...")
                df_alt = yf.download(alt_ticker, start="2024-01-01", end="2024-12-31", progress=False, auto_adjust=False)
                if not df_alt.empty:
                     logger.info(f"      ✨ FOUND with {alt_ticker}! (Suffix mismatch?)")
                else:
                     logger.error(f"      💀 Still empty.")
                     
        except Exception as e:
            logger.error(f"      💥 Exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
