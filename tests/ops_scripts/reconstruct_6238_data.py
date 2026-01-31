import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import yfinance as yf
import yfinance as yf
import pandas as pd
import json
import os
import glob
from datetime import datetime

# Configuration
STOCK_ID = "6238"
YF_TICKER = "6238.TWO"
START_YEAR = 2006
END_YEAR = 2026
DATA_DIR = "data/raw"

def get_yearly_prices(history):
    """
    Extract Start (First trading day) and End (Last trading day) prices for each year.
    Returns: dict { year: {'start': float, 'end': float} }
    """
    yearly_data = {}
    
    # Resample to Year Start/End could be tricky with gaps, 
    # so we group by year and pick first/last.
    history['Year'] = history.index.year
    
    for year, group in history.groupby('Year'):
        if year < START_YEAR or year > END_YEAR:
            continue
            
        # Use 'Close' price. 
        # Ideally Start Price = Open of first day? Or Close of first day?
        # System uses 'Close' typically for simplicity or 'Adj Close'?
        # Martian logic usually checks 'start' and 'end' from Market_{year}.json
        
        start_price = float(group.iloc[0]['Close'])
        end_price = float(group.iloc[-1]['Close'])
        
        yearly_data[year] = {
            "start": start_price,
            "end": end_price
        }
    return yearly_data

def get_yearly_dividends(ticker):
    """
    Extract dividends per year.
    Returns: dict { year: {'cash': float, 'stock': 0.0} }
    """
    divs = ticker.dividends
    yearly_divs = {}
    
    if divs.empty:
        return {}
        
    divs.index = pd.to_datetime(divs.index).tz_localize(None) # Remove timezone
    
    for date, amount in divs.items():
        year = date.year
        if year < START_YEAR:
            continue
            
        if year not in yearly_divs:
            yearly_divs[year] = {'cash': 0.0, 'stock': 0.0, 'date': date.strftime("%Y-%m-%d")}
            
        yearly_divs[year]['cash'] += float(amount)
        
    return yearly_divs

def inject_prices(price_data):
    print(f"Injecting Prices for {len(price_data)} years...")
    for year, prices in price_data.items():
        # Target TPEx file (since 6238 is TPEx)
        # If it doesn't exist, we create it? Or fallback to Market_{year}?
        # Safer to write to TPEx if it exists, or Market if not.
        # Actually crawler creates TPEx_Market_{year}_Prices.json.
        
        target_file = f"{DATA_DIR}/TPEx_Market_{year}_Prices.json"
        
        # Load existing
        data_map = {}
        if os.path.exists(target_file):
            try:
                with open(target_file, "r") as f:
                    data_map = json.load(f)
            except: pass
        else:
            # Try main Market file if TPEx missing (very old years?)
            pass 
            
        # Update
        data_map[STOCK_ID] = prices
        
        # Save
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(target_file, "w") as f:
            json.dump(data_map, f, indent=2)
            
        print(f"  -> Updated {target_file}: {prices}")

def inject_dividends(div_data):
    print(f"Injecting Dividends for {len(div_data)} years...")
    for year, div_info in div_data.items():
        # Using TPEx_Dividends_{year}.json
        target_file = f"{DATA_DIR}/TPEx_Dividends_{year}.json"
        
        # Load
        data_map = {}
        if os.path.exists(target_file):
            try:
                with open(target_file, "r") as f:
                    data_map = json.load(f)
            except: pass
            
        # Update
        # Format: "6238": {"cash": X, "stock": Y, "date": "..."}
        data_map[STOCK_ID] = div_info
        
        # Save
        with open(target_file, "w") as f:
            json.dump(data_map, f, indent=2)
            
        print(f"  -> Updated {target_file}: {div_info}")

def main():
    import requests
    import time
    
    tickers_to_try = [YF_TICKER, "6238.TW"]
    
    for ticker_name in tickers_to_try:
        print(f"Fetching data for {STOCK_ID} ({ticker_name})...")
        try:
            ticker = yf.Ticker(ticker_name)
            
            # 1. History
            hist = ticker.history(start=f"{START_YEAR}-01-01", end=f"{END_YEAR}-12-31")
            
            # Additional check for delisted/empty
            if hist.empty:
                print(f"WARNING: No history found for {ticker_name}")
                time.sleep(2)
                continue
                
            print(f"SUCCESS: Found {len(hist)} records for {ticker_name}")
            price_data = get_yearly_prices(hist)
            inject_prices(price_data)
            
            # 2. Dividends
            div_data = get_yearly_dividends(ticker)
            inject_dividends(div_data)
            
            print("Reconstruction Complete!")
            return
            
        except Exception as e:
             print(f"Error fetching {ticker_name}: {e}")
             time.sleep(2)

    print("ERROR: Failed to fetch data for 6238 with any suffix.")

if __name__ == "__main__":
    main()
