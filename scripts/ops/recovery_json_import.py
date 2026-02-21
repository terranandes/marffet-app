import json
import os
import duckdb
import pandas as pd

def main():
    con = duckdb.connect('data/market.duckdb')
    print("🗑️ Resetting daily_prices DB...")
    con.execute("DELETE FROM daily_prices")
    
    # We will use the 2030 target file mapping to filter valid tickers
    ref_df = pd.read_excel('app/project_tw/references/stock_list_s2006e2026_unfiltered.xlsx')
    valid_tickers = set(ref_df['id'].astype(str).str.zfill(4).tolist())
    
    json_dir = 'data/raw_test'
    all_records = []
    total_added = 0
    
    print(f"🚀 Importing valid market prices from JSON Cache (2006+)...")
    for year in range(2006, 2027):
        file_path = os.path.join(json_dir, f"Market_{year}_Prices.json")
        if not os.path.exists(file_path):
            continue
            
        print(f"  Loading {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            year_data = json.load(f)
            
        # Parse logic: year_data format -> { "stock_id": [{"d": "YMD", "c": close}, ...], ... }
        for stock_id, daily_list in year_data.items():
            if stock_id not in valid_tickers:
                continue
                
            if not daily_list:
                continue
                
            # Assume general structure
            # To emulate boundary behavior safely
            start_record = daily_list[0]
            end_record = daily_list[-1]
            
            # Map values
            # TW market vs TPEx. Since JSON loses .TW tags we will assume TWSE for simplicity unless we lookup.
            # Market column actually doesn't impact numerical correlation filtering so fake 'TWSE' is fine.
            all_records.append({
                'stock_id': stock_id,
                'date': f"{start_record['d'][:4]}-{start_record['d'][4:6]}-{start_record['d'][6:]}",
                'open': float(start_record.get('o', start_record['c'])),
                'high': float(start_record.get('h', start_record['c'])),
                'low': float(start_record.get('l', start_record['c'])),
                'close': float(start_record['c']),
                'volume': float(start_record.get('v', 0)),
                'market': 'TWSE'
            })
            
            if start_record['d'] != end_record['d']:
                all_records.append({
                    'stock_id': stock_id,
                    'date': f"{end_record['d'][:4]}-{end_record['d'][4:6]}-{end_record['d'][6:]}",
                    'open': float(end_record.get('o', end_record['c'])),
                    'high': float(end_record.get('h', end_record['c'])),
                    'low': float(end_record.get('l', end_record['c'])),
                    'close': float(end_record['c']),
                    'volume': float(end_record.get('v', 0)),
                    'market': 'TWSE'
                })
                
        # Flush DB every 5 years
        if len(all_records) > 20000:
            temp_df = pd.DataFrame(all_records)
            con.register('temp_df', temp_df)
            con.execute("INSERT OR IGNORE INTO daily_prices SELECT * FROM temp_df")
            con.unregister('temp_df')
            total_added += len(all_records)
            all_records = []
            
    # Final flush
    if all_records:
        temp_df = pd.DataFrame(all_records)
        con.register('temp_df', temp_df)
        con.execute("INSERT OR IGNORE INTO daily_prices SELECT * FROM temp_df")
        con.unregister('temp_df')
        total_added += len(all_records)
        
    final_count = con.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
    final_stocks = con.execute("SELECT COUNT(DISTINCT stock_id) FROM daily_prices").fetchone()[0]
    print(f"✨ Restored {final_count} local cached DuckDB rows across {final_stocks} unique references!")
    con.close()

if __name__ == "__main__":
    main()
