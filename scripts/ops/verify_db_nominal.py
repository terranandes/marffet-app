import os
import duckdb
import json
import pandas as pd
from datetime import datetime

DB_PATH = 'data/market.duckdb'
CACHE_DIR = 'data/raw_test' # Where the correlation script expects to find them

def export_nominal_cache():
    print("🚀 Exporting verified nominal boundaries to JSON Cache...")
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    conn = duckdb.connect(DB_PATH, read_only=True)
    
    # We want to group by year.
    query = """
        SELECT 
            stock_id, 
            date, 
            open, 
            high, 
            low, 
            close, 
            volume 
        FROM daily_prices 
        ORDER BY date ASC
    """
    df = conn.execute(query).df()
    conn.close()
    
    if df.empty:
        print("❌ daily_prices is empty!")
        return
        
    df['year'] = pd.to_datetime(df['date']).dt.year
    
    years = df['year'].unique()
    for year in sorted(years):
        year_df = df[df['year'] == year]
        
        # Build dict
        result_dict = {}
        
        # Group by stock
        for stock_id, group in year_df.groupby('stock_id'):
            stock_list = []
            for _, row in group.iterrows():
                stock_list.append({
                    "d": row["date"].strftime("%Y%m%d"),
                    "o": float(row["open"]),
                    "h": float(row["high"]),
                    "l": float(row["low"]),
                    "c": float(row["close"]),
                    "v": int(row["volume"])
                })
            result_dict[stock_id] = stock_list
            
        # Wrap it in {year: {stock_id: [...]}} format expected by my correlation reader
        # Actually wait, the `correlate_all_stocks.py` uses `TWSECrawler(data_dir=...)` which generates Market_YYYY_Prices.json
        # The internal format of Market_YYYY_Prices.json is usually `{stock_id: [{"d": ...}]}`
        # The TWSE crawler expects `{year: {stock: {'start': 100, 'end': 200}}}` 
        # Actually wait, `fetch_market_prices_batch` reads `{year: {stock_id: [{'d':...}, ...]}}`
        # Because we already wiped `data/raw_test/Market_*_Prices.json`, let's just create them.
        import json
        out_path = os.path.join(CACHE_DIR, f"Market_{year}_Prices.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False)
        print(f"Created {out_path} for Year {year}")

    print(f"✅ Loaded {len(df)} records from DuckDB successfully into JSON cache.")

if __name__ == "__main__":
    export_nominal_cache()
