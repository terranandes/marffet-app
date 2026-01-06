import pandas as pd
import yfinance as yf
import json
import os
import time

# 1. Load Stock List
print("Loading stock list...")
df = pd.read_excel("project_tw/output/stock_list_s2006e2025_filtered.xlsx")
stock_ids = df['id'].unique().tolist()
print(f"Total stocks to process: {len(stock_ids)}")

# 2. Output File
OUTPUT_FILE = "data/dividends_all.json"
data = {}

# Load existing if available (resume capability)
if os.path.exists(OUTPUT_FILE):
    try:
        with open(OUTPUT_FILE, "r") as f:
            data = json.load(f)
        print(f"Loaded {len(data)} existing records.")
    except:
        print("Could not load existing data, starting fresh.")

# 3. Fetch Loop
count = 0
for stock_id in stock_ids:
    stock_id_str = str(stock_id)
    if stock_id_str in data:
        continue # Skip already fetched
        
    ticker_symbol = f"{stock_id_str}.TW"
    print(f"[{count+1}/{len(stock_ids)}] Fetching {ticker_symbol}...", end="", flush=True)
    
    try:
        t = yf.Ticker(ticker_symbol)
        # Fetch actions (Dividends + Splits)
        actions = t.actions
        
        # Filter from 2006
        try:
             actions = actions[actions.index >= '2006-01-01']
        except:
             # If index invalid or empty
             pass
        
        # Process into simulated format
        # Structure: { 2006: { 'cash': 2.5, 'stock': 0.5 }, ... }
        # Note: yfinance Actions index is Date. We need to aggregate by YEAR?
        # Or keep by Date? Simulation currently runs yearly.
        # Aggregating by Year is safer for our simplistic model.
        
        yearly_data = {}
        
        for date, row in actions.iterrows():
            year = date.year
            if year not in yearly_data:
                yearly_data[year] = {'cash': 0.0, 'stock_split': 1.0}
            
            # Cash Dividend
            if 'Dividends' in row and row['Dividends'] > 0:
                yearly_data[year]['cash'] += row['Dividends']
            
            # Stock Split/Dividend
            # In TW: 1.05 split means 50 shares per 1000.
            # We accumulate splits (product?) or sum?
            # Splits are usually point-in-time multipliers.
            if 'Stock Splits' in row and row['Stock Splits'] > 0 and row['Stock Splits'] != 1.0:
                 yearly_data[year]['stock_split'] *= row['Stock Splits']
        
        # Store
        data[stock_id_str] = yearly_data
        print(f" OK ({len(yearly_data)} yrs)")
        
        # Save every 10
        if count % 10 == 0:
             with open(OUTPUT_FILE, "w") as f:
                json.dump(data, f, indent=4)
                
    except Exception as e:
        print(f" FAIL: {e}")
        # Save empty to avoid retry loop death, or just skip?
        # Better to save empty struct so we know we tried.
        data[stock_id_str] = {}
        
    count += 1
    # Rate limit nice-ness
    time.sleep(0.5)

# Final Save
with open(OUTPUT_FILE, "w") as f:
    json.dump(data, f, indent=4)
print("Done!")
