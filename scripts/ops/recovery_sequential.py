import yfinance as yf
import pandas as pd
import duckdb
import os
import time
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

DB_PATH = 'data/market.duckdb'

def process_symbol(t: str) -> List[tuple]:
    def try_download(symbol):
        df = yf.download(symbol, period="max", auto_adjust=False, progress=False)
        return df if not df.empty and 'Date' in df.reset_index().columns else None

    try:
        time.sleep(0.5)
        # Try TWSE first, then TPEx
        df = try_download(f"{t}.TW")
        if df is None:
            df = try_download(f"{t}.TWO")
            
        if df is None:
            return []
            
        df = df.reset_index()
        cols = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df.columns = cols
        
        if 'Date' not in df.columns: return []
        
        insert_data = []
        for _, row in df.iterrows():
            try:
                c = float(row['Close'])
                if c > 0:
                    insert_data.append((
                        t, 
                        row['Date'].date(),
                        float(row['Open']),
                        float(row['High']),
                        float(row['Low']),
                        c,
                        int(float(row['Volume'])),
                        None
                    ))
            except Exception:
                pass
        return insert_data
    except Exception as e:
        return []

def fetch_nominal_recovery_data():
    conn = duckdb.connect(DB_PATH)
    
    # Get all tickers from our reference list instead of guessing
    df_ref = pd.read_excel('app/project_tw/references/stock_list_s2006e2026_unfiltered.xlsx')
    tickers = [str(t).zfill(4) for t in df_ref['id'].tolist() if pd.notna(t)]
    
    print(f"🚀 Multithreaded Recovery: {len(tickers)} reference stocks...")
    
    print("🗑️ Emptying daily_prices table...")
    conn.execute("DELETE FROM daily_prices")
    conn.execute("CHECKPOINT")
    
    total_inserted = 0
    completed = 0
    
    # 5 workers is usually safe for YF before getting outright blocked
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_symbol, str(t)): str(t) for t in tickers}
        
        for future in as_completed(futures):
            t = futures[future]
            completed += 1
            try:
                records = future.result()
                if records:
                    conn.executemany("""
                        INSERT OR IGNORE INTO daily_prices (stock_id, date, open, high, low, close, volume, market)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, records)
                    total_inserted += len(records)
            except Exception as e:
                pass
                
            if completed % 50 == 0:
                print(f"✅ [{completed}/{len(tickers)}] Total Inserted: {total_inserted}")
                # Commit occasionally
                conn.execute("CHECKPOINT")
                
    print(f"\n✨ Full Market Recovery Complete. Total true daily nominal rows: {total_inserted}")
    conn.close()

if __name__ == "__main__":
    fetch_nominal_recovery_data()
