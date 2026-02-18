
import json
import os
import sys
import time
import yfinance as yf
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

DATA_DIR = "data/raw_dividends"
PATCH_FILE = "data/ref/ky_dividend_patch.json"

def get_ky_dr_stocks():
    """Identify KY/DR stocks from the reference list."""
    stock_list_path = "app/project_tw/references/stock_list_s2006e2026_unfiltered.xlsx"
    if not os.path.exists(stock_list_path):
        print(f"❌ Reference file not found: {stock_list_path}")
        return {}

    print(f"🔍 Scanning stock list from {stock_list_path}...")
    try:
        df = pd.read_excel(stock_list_path)
        # Assuming columns 'id' and 'name' exist based on previous tasks
        # Convert id to string just in case
        df['id'] = df['id'].astype(str).str.zfill(4) # Ensure 4 digits? Or just string
        
        targets = {}
        for _, row in df.iterrows():
            name = str(row['name'])
            code = str(row['id'])
            
            # Smart cleanup of code
            if len(code) > 4 and code.endswith('.TW'): code = code.replace('.TW', '')
            
            if 'KY' in name or 'DR' in name or '*' in name:
                targets[code] = name
                
        print(f"✅ Found {len(targets)} unique KY/DR/* stocks.")
        return targets
    except Exception as e:
        print(f"❌ Error reading stock list: {e}")
        return {}

def fetch_yf_data(stock_id):
    """Fetch Dividends (Cash) and Splits (Stock) from YFinance."""
    symbol = f"{stock_id}.TW"
    try:
        t = yf.Ticker(symbol)
        
        # Fetch history (max to get all events)
        # We need dividends and splits
        divs = t.dividends
        splits = t.splits
        
        # Convert to year-based dict
        # Structure: {year: {'cash': sum, 'stock': sum}}
        # Note: YFinance reports Split Ratio (e.g. 1.05 for 5% stock div, or 2.0 for 2-for-1)
        # We need to convert Split Ratio to Stock Dividend value.
        # Rule: Stock Div = (SplitRatio - 1) * 10 ?? 
        # Wait, TWT49U 'stock' is usually in TWD (par 10) or Shares/1000?
        # In martian, stock dividend 1.0 means 100 shares per 1000 shares (10%).
        # YF Split 1.1 means 10% increase.
        # So StockDiv = (Split - 1) * 10.
        
        yearly_data = {}
        
        # Process Cash Dividends
        if not divs.empty:
            # Group by year
            # Ensure timezone naive or UTC
            divs.index = divs.index.tz_convert(None)
            by_year = divs.groupby(divs.index.year).sum()
            
            for year, val in by_year.items():
                if year not in yearly_data: yearly_data[year] = {'cash': 0.0, 'stock': 0.0}
                yearly_data[year]['cash'] = float(val)
                
        # Process Stock Splits -> Stock Dividends
        if not splits.empty:
            splits.index = splits.index.tz_convert(None)
            # Filter standard splits?
            # 2330 has 1.005 -> 0.5% stock div -> 0.05
            # 4763 has 10.0 -> 1-to-10 split? Or par value change?
            # If split > 2.0, it's likely a par change or massive split, generally treated as 'stock dividend' in adjustment?
            # Actually, `calculator.py` treats stock div as `(stock_val / 10)`.
            # If Split is 1.1, new price = old / 1.1.
            # If StockDiv is 1.0 (10%), new price = old / (1 + 1.0/10) = old / 1.1.
            # So Formula: StockVal = (SplitRatio - 1) * 10
            
            for date, ratio in splits.items():
                if ratio <= 1.0: continue 
                year = date.year
                
                # Check for magnitude
                # If ratio is huge (e.g. 10.0), it might be 1000% stock dividend??
                # Or Par Value change 10 -> 1 (Shares x10).
                # In both cases, the adjustment factor is dividing price by 10.
                # So (10 - 1) * 10 = 90 ??
                # Let's verify 2330: Split 1.005 -> (1.005 - 1)*10 = 0.05. Correct (0.5% stock div).
                
                stock_val = (ratio - 1) * 10
                
                # Cap extremely large splits (likely par value changes, e.g. 10-to-1)
                # 20.0 corresponds to a 3-for-1 split (ratio 3.0) -> (3-1)*10 = 20.
                if stock_val > 20.0:
                    print(f"  ⚠️  Capping large split for {symbol} date={date.date()} ratio={ratio} val={stock_val:.2f} -> 20.0")
                    stock_val = 20.0
                
                if year not in yearly_data: yearly_data[year] = {'cash': 0.0, 'stock': 0.0}
                yearly_data[year]['stock'] += stock_val
                
        return yearly_data

    except Exception as e:
        print(f"  ❌ YF Error {stock_id}: {e}")
        return None

def main():
    targets = get_ky_dr_stocks()
    patch_data = {}
    
    print(f"🚀 Fetching data for {len(targets)} stocks from YFinance...")
    
    for i, (stock_id, name) in enumerate(targets.items()):
        print(f"[{i+1}/{len(targets)}] {stock_id} {name}...", end='\r')
        
        yf_data = fetch_yf_data(stock_id)
        
        if yf_data:
            patch_data[stock_id] = {
                'name': name,
                'source': 'yfinance',
                'updated': datetime.now().isoformat(),
                'dividends': yf_data
            }
            # print(f"  ✅ {stock_id}: {len(yf_data)} years")
        else:
            # print(f"  ⚠️  No data for {stock_id}")
            pass
            
        # Rate limit protection (YFinance can be strict)
        if i % 10 == 0: time.sleep(1)
            
    print(f"\n✅ Stats: Fetched {len(patch_data)} stocks.")
    
    # Save
    with open(PATCH_FILE, 'w') as f:
        json.dump(patch_data, f, indent=2, sort_keys=True)
    print(f"💾 Saved patch to {PATCH_FILE}")

if __name__ == "__main__":
    main()
