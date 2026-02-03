
import json
import logging
import time
import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("crawler_official.log"), logging.StreamHandler()]
)

# Paths
BASE_DIR = Path("/home/terwu01/github/martian")
DATA_DIR = BASE_DIR / "data/raw"
# Switch to Unfiltered List as "Formal Source"
EXCEL_PATH = BASE_DIR / "app/project_tw/references/stock_list_s2006e2026_unfiltered.xlsx"

def load_all_stocks():
    """
    Fetch Active Stocks directly from TWSE ISIN (Formal Source).
    Modes: 2 (Listed), 4 (OTC).
    Filter: 4-digit codes only (Common Stocks + Major ETFs).
    """
    import httpx
    import re
    
    codes = set()
    modes = [2, 4]
    logging.info("Fetching formal stock list from isin.twse.com.tw...")
    
    for m in modes:
        try:
            url = f"https://isin.twse.com.tw/isin/C_public.jsp?strMode={m}"
            # Use sync httpx
            resp = httpx.get(url, timeout=30)
            text = resp.content.decode('big5', errors='ignore')
            
            # Pattern: >(Code) (Name)</td>
            # matches "1101　台泥"
            matches = re.findall(r'>([A-Z0-9]{4,6})[ \u3000]+([^<]+)</td>', text)
            
            count = 0
            for code, name in matches:
                code = code.strip()
                # filtering we defined: 4 digits (Stocks)
                if len(code) == 4:
                    codes.add(code)
                    count += 1
            logging.info(f"Mode {m}: Found {count} valid codes.")
        except Exception as e:
            logging.error(f"ISIN Fetch Error Mode {m}: {e}")
            
    sorted_codes = sorted(list(codes))
    logging.info(f"Total Unique Active Stocks: {len(sorted_codes)}")
    return sorted_codes

def update_json_file(year: int, new_data: dict):
    fpath = DATA_DIR / f"Market_{year}_Prices.json"
    current_data = {}
    if fpath.exists():
        try:
            with open(fpath, 'r') as f:
                current_data = json.load(f)
        except:
            pass
    
    current_data.update(new_data)
    with open(fpath, 'w') as f:
        json.dump(current_data, f, separators=(',', ':'))

def fetch_unadjusted_history(stock_id: str):
    suffixes = ['.TW', '.TWO']
    df = pd.DataFrame()
    
    for suffix in suffixes:
        ticker_name = f"{stock_id}{suffix}"
        try:
            t = yf.Ticker(ticker_name)
            # auto_adjust=False is CRITICAL
            hist = t.history(start="2006-01-01", end="2026-12-31", auto_adjust=False)
            
            if not hist.empty:
                df = hist
                # Debug Check for TSMC 2006
                if stock_id == '2330':
                    first_open = df.iloc[0]['Open']
                    logging.info(f"DEBUG: TSMC 2006-01-02 Open: {first_open} (Should be ~59)")
                break
        except Exception as e:
            continue

            
    if df.empty:
        return {}
        
    # Process into Martian Format
    # { Year: { stock_id: Node } }
    results_by_year = {}
    
    # Ensure index is datetime
    df.index = pd.to_datetime(df.index)
    
    years = df.index.year.unique()
    for year in years:
        year_data = df[df.index.year == year]
        if year_data.empty: continue
        
        # Unadjusted Prices
        # yfinance columns: Open, High, Low, Close, Volume, Dividends, Stock Splits
        
        first = year_data.iloc[0]
        last = year_data.iloc[-1]
        
        # 1. Build Yearly Summary (Fast Path)
        summary = {
            "id": stock_id,
            "name": stock_id,
            "start": float(first['Open']), 
            "end": float(last['Close']),
            "high": float(year_data['High'].max()),
            "low": float(year_data['Low'].min()),
            "volume": int(year_data['Volume'].sum()),
            "first_open": float(first['Open'])
        }
        
        # 2. Build Daily List (High-Res Path)
        daily_list = []
        for timestamp, row in year_data.iterrows():
            # timestamp is pd.Timestamp
            daily_list.append({
                "d": timestamp.strftime('%Y-%m-%d'),
                "o": round(float(row['Open']), 2),
                "h": round(float(row['High']), 2),
                "l": round(float(row['Low']), 2),
                "c": round(float(row['Close']), 2),
                "v": int(row['Volume'])
            })

        # Verify Integrity (Safety Check)
        if stock_id == '2330' and year == 2006 and summary['start'] < 50:
            logging.critical(f"INTEGRITY FAILURE: {stock_id} 2006 Price {summary['start']} seems Adjusted! Expected > 50")
            
        # Clean NaNs in Summary
        for k, v in summary.items():
            if pd.isna(v): summary[k] = 0
            
        results_by_year[int(year)] = {
            "id": stock_id,
            "summary": summary,
            "daily": daily_list
        }
        
    return results_by_year

def main():
    stocks = load_all_stocks()
    logging.info(f"Loaded {len(stocks)} stocks from Filtered List.")
    
    
    # Test Run or Full Run?
    # User said "Proceed Phase 2 Scraper". We should cycle them all.
    # But let's batch it.
    
    buffer = {}
    count = 0
    success = 0
    
    for stock_id in stocks:
        count += 1
        if count % 10 == 0:
            print(f"Progress: {count}/{len(stocks)} (Success: {success})")
            
        res = fetch_unadjusted_history(stock_id)
        if res:
            success += 1
            for year, node in res.items():
                if year not in buffer: buffer[year] = {}
                buffer[year][stock_id] = node
        else:
            logging.warning(f"Failed to fetch {stock_id}")
            
        # Optimization: Flush every 50 stocks
        if len(buffer) > 0 and count % 50 == 0:
            for y, d in buffer.items():
                update_json_file(y, d)
            buffer = {}
            
    # Final Flush
    if buffer:
        for y, d in buffer.items():
            update_json_file(y, d)
            
    logging.info(f"Completed. Success Rate: {success}/{len(stocks)}")

if __name__ == "__main__":
    main()
