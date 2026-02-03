
import json
import logging
import time
from pathlib import Path
from datetime import datetime
import yfinance as yf
import pandas as pd

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("crawler.log"), logging.StreamHandler()]
)

# Paths
BASE_DIR = Path("/home/terwu01/github/martian")
DATA_DIR = BASE_DIR / "data/raw"
TARGET_LIST_PATH = BASE_DIR / "data/target_crawl_list.json"

def load_target_list():
    with open(TARGET_LIST_PATH, 'r') as f:
        return json.load(f)

def get_market_file_path(year: int):
    # Determine if it's TWSE or OTC?
    # Actually, we have split files: Market_{year} (TWSE) and TPEx_Market_{year} (OTC).
    # Since we don't know the market for sure for the missing stocks, we might default to one or check.
    # Strategy: Try to append to `Market_{year}_Prices.json` by default, or better, 
    # since we don't distinguish in the input list, we can write to `Market_{year}_Prices.json`.
    # Ideally we should know which market.
    # yfinance suffixes: .TW (TWSE), .TWO (OTC).
    # We will try both if one fails, or just try .TW first.
    return DATA_DIR / f"Market_{year}_Prices.json"

def update_json_file(year: int, new_data: dict):
    """
    Atomic update of the JSON file.
    new_data: { stock_id: { ...data... } }
    """
    fpath = get_market_file_path(year)
    current_data = {}
    
    if fpath.exists():
        try:
            with open(fpath, 'r') as f:
                current_data = json.load(f)
        except json.JSONDecodeError:
            logging.error(f"Corrupt JSON file: {fpath}")
            
    # Update
    current_data.update(new_data)
    
    # Write back
    with open(fpath, 'w') as f:
        json.dump(current_data, f, separators=(',', ':')) # Minimize size

def fetch_stock_history(stock_id: str):
    """
    Fetch 2006-2026 data for a stock.
    Returns a dict grouped by year: { 2023: { ... }, 2024: { ... } }
    """
    suffixes = ['.TW', '.TWO']
    df = pd.DataFrame()
    found_suffix = ""

    for suffix in suffixes:
        ticker = f"{stock_id}{suffix}"
        try:
            # Download full history
            data = yf.download(ticker, start="2006-01-01", end="2026-12-31", progress=False)
            if not data.empty:
                df = data
                found_suffix = suffix
                break
        except Exception as e:
            logging.warning(f"Failed to fetch {ticker}: {e}")
            
    if df.empty:
        logging.warning(f"No data found for {stock_id} with suffixes {suffixes}")
        return {}

    # Process Data
    # Group by Year
    results_by_year = {}
    
    # Reset index to get Date column
    df = df.reset_index()
    
    # Ensure columns are flat (yfinance sometimes returns MultiIndex)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    # Standardize column names
    df.columns = [c.lower() for c in df.columns]
    
    # Iterate through years in the data
    years = df['date'].dt.year.unique()
    
    for year in years:
        year_data = df[df['date'].dt.year == year]
        if year_data.empty:
            continue
            
        # Extract OHLCV summary for the year?
        # WAIT. The JSON format in Market_YYYY_Prices.json - what is it?
        # Let's check the schema.
        # Usually it stores: { "stock_id": { "start": ..., "end": ..., "high": ..., "low": ... } }
        # Or detailed daily data?
        # Based on previous content, it seems to store SUMMARY data for the year.
        # "first_open", "end", "high", "low".
        
        first_row = year_data.iloc[0]
        last_row = year_data.iloc[-1]
        
        # Calculate Year High/Low
        year_high = year_data['high'].max()
        year_low = year_data['low'].min()
        
        # Prepare Node
        node = {
            "id": stock_id,
            "name": stock_id, # We don't have name from excel easily, use ID
            "start": float(first_row['open']), # Open of first day
            "end": float(last_row['close']),   # Close of last day
            "high": float(year_high),
            "low": float(year_low),
            "volume": int(year_data['volume'].sum()),
            "first_open": float(first_row['open']) # Redundant but consistent
        }
        
        # Clean NaNs
        for k, v in node.items():
            if pd.isna(v):  node[k] = 0
            
        results_by_year[int(year)] = node
        
    return results_by_year

def main():
    target_stocks = load_target_list()
    logging.info(f"Starting crawl for {len(target_stocks)} stocks...")
    
    # Limit for sample run (Estimate recovery rate)
    target_stocks = target_stocks[:20] 
    logging.info(f"Sample Run: crawling {len(target_stocks)} stocks to estimate recovery rate...")
    
    # We will buffer updates to minimize file I/O
    # buffer: { year: { stock_id: node } }
    buffer = {} 
    
    count = 0
    for stock_id in target_stocks:
        count += 1
        stock_id = str(stock_id).strip()
        
        logging.info(f"[{count}/{len(target_stocks)}] Fetching {stock_id}...")
        
        stock_results = fetch_stock_history(stock_id)
        
        if stock_results:
            for year, node in stock_results.items():
                if year not in buffer:
                    buffer[year] = {}
                buffer[year][stock_id] = node
        
        # Rate Limiting / Sleep (yfinance is nice but don't abuse)
        # 3 req / 10s = ~3.3s per req? yfinance might trigger multiples.
        # Let's sleep 1s.
        time.sleep(1.0)
        
        # Flush every 10 stocks or at end
        if count % 10 == 0:
            flush_buffer(buffer)
            buffer = {}
            
    # Final flush
    if buffer:
        flush_buffer(buffer)
        
    logging.info("Crawl completed.")

def flush_buffer(buffer):
    logging.info("Flushing buffer to disk...")
    for year, stock_map in buffer.items():
        update_json_file(year, stock_map)

if __name__ == "__main__":
    main()
