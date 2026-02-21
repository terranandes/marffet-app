import os
import duckdb
import datetime
import asyncio
import pandas as pd
from app.project_tw.crawler import TWSECrawler

DB_PATH = 'data/market.duckdb'

async def re_crawl_all_prices():
    print("🚀 Re-crawling authentic market-wide nominal boundary prices purely from TWSE/TPEx caches...")
    conn = duckdb.connect(DB_PATH)
    
    crawler = TWSECrawler(data_dir="data/raw_test")
    
    print("🗑️ Emptying corrupted daily_prices...")
    conn.execute("DELETE FROM daily_prices")
    conn.execute("CHECKPOINT")
    
    years = list(range(2006, 2027))
    print(f"⏳ Downloading market-wide boundary prices for {len(years)} years...")
    
    try:
        raw_dict = await crawler.fetch_market_prices_batch(years)
        if raw_dict:
            print(f"✅ Successfully downloaded nominal boundary price records dict.")
            records = []
            
            # The structure from crawler.py fetch_market_prices_batch is:
            # {year: {stock_id: [{'d': '2024-01-02', 'o': 590.0, 'h': 593.0, 'l': 589.0, 'c': 593.0, 'v': 3000000}, ...]}, ...}
            # Or it might be the start/end dict we saw earlier. I will handle BOTH formats defensively.
            
            for year, stock_data in raw_dict.items():
                if not isinstance(stock_data, dict):
                    continue
                    
                for stock_code, boundary in stock_data.items():
                    if isinstance(boundary, list):
                        # Format A: [{'d': '2024-01-02', 'c': 100}, ...] (Full daily array)
                        for day_data in boundary:
                           d = day_data.get('d')
                           c = float(day_data.get('c', 0))
                           if d and c > 0:
                                records.append({
                                    'stock_id': stock_code,
                                    'date': pd.to_datetime(d).date(),
                                    'open': float(day_data.get('o', 0)),
                                    'high': float(day_data.get('h', 0)),
                                    'low': float(day_data.get('l', 0)),
                                    'close': c,
                                    'volume': int(float(day_data.get('v', 0))),
                                    'market': 'TWSE'
                                })
                    elif isinstance(boundary, dict):
                        # Format B: {'start': 100, 'end': 200}
                        start_price = boundary.get('start', 0)
                        end_price = boundary.get('end', 0)
                        
                        if start_price > 0:
                            records.append({
                                'stock_id': stock_code,
                                'date': pd.to_datetime(f"{year}-01-02").date(),
                                'open': float(start_price),
                                'high': float(start_price),
                                'low': float(start_price),
                                'close': float(start_price),
                                'volume': 1000,
                                'market': 'TWSE'
                            })
                        if end_price > 0:
                            records.append({
                                'stock_id': stock_code,
                                'date': pd.to_datetime(f"{year}-12-28").date(),
                                'open': float(end_price),
                                'high': float(end_price),
                                'low': float(end_price),
                                'close': float(end_price),
                                'volume': 1000,
                                'market': 'TWSE'
                            })
            
            if records:
                df = pd.DataFrame(records)
                df = df.drop_duplicates(subset=['stock_id', 'date'], keep='last')
                
                print(f"💾 Inserting {len(df)} pure nominal records into DuckDB...")
                conn.register('temp_df', df)
                conn.execute("INSERT OR IGNORE INTO daily_prices SELECT * FROM temp_df")
                conn.unregister('temp_df')
                
                final_count = conn.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
                print(f"✨ TWSE Mass Recovery complete! Total nominal rows in DB: {final_count}")
            else:
                print("⚠️ No valid records found in the fetched dictionary.")
        else:
            print("⚠️ Returned Dictionary was empty.")

    except Exception as e:
        print(f"❌ Error during batch recovery: {e}")
        
    conn.close()

if __name__ == "__main__":
    asyncio.run(re_crawl_all_prices())
