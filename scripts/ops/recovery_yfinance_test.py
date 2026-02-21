import os
import duckdb
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
import time

DB_PATH = 'data/market.duckdb'

def fetch_nominal_prices(ticker):
    # Try .TW and .TWO suffixes
    for suffix in ['.TW', '.TWO']:
        try:
            full_ticker = f"{ticker}{suffix}"
            t = yf.Ticker(full_ticker)
            # CRITICAL: auto_adjust=False, actions=False ensures we get pure NOMINAL prices
            hist = t.history(period="max", auto_adjust=False, actions=False)
            if not hist.empty:
                records = []
                for date, row in hist.iterrows():
                    d_str = date.strftime('%Y-%m-%d')
                    records.append({
                        'stock_id': ticker,
                        'date': pd.to_datetime(d_str).date(),
                        'open': float(row['Open']),
                        'high': float(row['High']),
                        'low': float(row['Low']),
                        'close': float(row['Close']),
                        'volume': int(row['Volume']),
                        'market': 'TWSE' if suffix == '.TW' else 'TPEx'
                    })
                return records
        except Exception:
            pass
    return []

# Fetch a robust list of stock tickers from the existing cache
def get_tickers():
    import json
    tickers = []
    try:
        with open('data/ref/goodinfo_dividends.json', 'r') as f:
            data = json.load(f)
            tickers = list(data.keys())
    except:
        pass
    return tickers

def main():
    print("🚀 Mass-recovering pure nominal prices from YFinance (auto_adjust=False)...")
    tickers = get_tickers()
    if not tickers:
        print("❌ No tickers found. Aborting.")
        return
        
    print(f"📊 Processing {len(tickers)} tickers for full max history...")
    
    conn = duckdb.connect(DB_PATH)
    print("🗑️ Emptying corrupted daily_prices...")
    conn.execute("DELETE FROM daily_prices")
    conn.execute("CHECKPOINT")
    
    all_records = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        from tqdm import tqdm
        try:
            results = list(tqdm(executor.map(fetch_nominal_prices, tickers), total=len(tickers)))
        except ImportError:
            # Fallback if tqdm is deleted
            results = list(executor.map(fetch_nominal_prices, tickers))
            
    for r in results:
        if r:
            all_records.extend(r)
            
    if all_records:
        df = pd.DataFrame(all_records)
        df = df.drop_duplicates(subset=['stock_id', 'date'])
        
        print(f"\n💾 Inserting {len(df)} pure nominal rows into DuckDB...")
        conn.register('temp_df', df)
        conn.execute("INSERT OR IGNORE INTO daily_prices SELECT * FROM temp_df")
        conn.unregister('temp_df')
        
        final_count = conn.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
        print(f"✨ YFinance Nominal Recovery complete! Total DB rows: {final_count}")
    else:
        print("\n⚠️ YFinance returned 0 valid nominal records.")
    
    conn.close()

if __name__ == "__main__":
    main()
