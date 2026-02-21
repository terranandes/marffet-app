import os
import json
import duckdb
import glob
import pandas as pd

DB_PATH = 'data/market.duckdb'
RAW_DIR = 'data/raw'

def rebuild_from_cache():
    json_files = glob.glob(f"{RAW_DIR}/Market_*_Prices.json")
    json_files.extend(glob.glob(f"{RAW_DIR}/TPEx_Market_*_Prices.json"))
    
    if not json_files:
        print("❌ No JSON cache files found!")
        return
        
    print(f"📖 Found {len(json_files)} JSON cache files.")
    
    conn = duckdb.connect(DB_PATH)
    print("🗑️ Emptying daily_prices table to flush all corrupted data...")
    conn.execute("DELETE FROM daily_prices")
    
    total_inserted = 0
    
    for fpath in sorted(json_files):
        print(f"⏳ Loading {os.path.basename(fpath)} via Pandas...")
        with open(fpath, 'r') as f:
            data = json.load(f)
            
        records = []
        
        def extract_records(stock_id, day_list):
            if not isinstance(day_list, list): return
            for ohlcv in day_list:
                date_str = ohlcv.get("d")
                if not date_str: continue
                c = float(ohlcv.get("c", 0))
                if c > 0:
                    records.append({
                        'stock_id': stock_id,
                        'date': pd.to_datetime(date_str).date(),
                        'open': float(ohlcv.get("o", 0)),
                        'high': float(ohlcv.get("h", 0)),
                        'low': float(ohlcv.get("l", 0)),
                        'close': c,
                        'volume': int(float(ohlcv.get("v", 0))),
                        'market': None
                    })

        for key, value in data.items():
            if isinstance(value, list):
                extract_records(key, value)
            elif isinstance(value, dict):
                for stock_id, day_list in value.items():
                    extract_records(stock_id, day_list)
                    
        if records:
            df = pd.DataFrame(records)
            # Drop duplicates keeping the last one seen just in case of overlaps
            df = df.drop_duplicates(subset=['stock_id', 'date'], keep='last')
            
            # Using DuckDB's fast register & append
            conn.register('temp_df', df)
            conn.execute("INSERT OR IGNORE INTO daily_prices SELECT * FROM temp_df")
            conn.unregister('temp_df')
            
            total_inserted += len(df)
            print(f"  ✅ Inserted {len(df)} rows")
            
    print(f"✅ DB Rebuild Complete! Automatically inserted {total_inserted} true historical daily records.")
    
    # Spot check 8066
    print("\n🔍 Spot Check - 8066 (Should NOT be 8.02):")
    print(conn.execute("SELECT * FROM daily_prices WHERE stock_id='8066' ORDER BY date LIMIT 5").df())

    conn.close()

if __name__ == "__main__":
    rebuild_from_cache()
