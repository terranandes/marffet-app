import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import asyncio
from app.project_tw.crawler import TWSECrawler
from app.project_tw.crawler_tpex import TPEXCrawler
import duckdb
import pandas as pd
from datetime import datetime

async def fetch_bounds():
    con = duckdb.connect('data/market.duckdb')
    print("🗑️ Resetting daily_prices DB...")
    con.execute("DELETE FROM daily_prices")
    
    ref_df = pd.read_excel('app/project_tw/references/stock_list_s2006e2026_unfiltered.xlsx')
    valid_tickers = set(ref_df['id'].astype(str).str.zfill(4).tolist())
    
    twse_crawler = TWSECrawler()
    tpex_crawler = TPEXCrawler()
    
    years_to_fetch = list(range(2006, 2027))
    print(f"🚀 Fetching TWSE start/end prices for years {years_to_fetch[0]} to {years_to_fetch[-1]}...")
    twse_results = await twse_crawler.fetch_market_prices_batch(years_to_fetch)
    
    print(f"🚀 Fetching TPEx start/end prices for years {years_to_fetch[0]} to {years_to_fetch[-1]}...")
    tpex_results = await tpex_crawler.fetch_market_prices_batch(years_to_fetch)
    
    all_records = []
    
    # Process TWSE
    for year, year_data in twse_results.items():
        if not year_data: continue
        for code, bounds in year_data.items():
            if code not in valid_tickers: continue
            start_p = float(bounds.get('start', 0.0))
            end_p = float(bounds.get('end', 0.0))
            if start_p > 0: all_records.append({'stock_id': code, 'date': f"{year}-01-02", 'open': start_p, 'high': start_p, 'low': start_p, 'close': start_p, 'volume': 0, 'market': 'TWSE'})
            if end_p > 0: all_records.append({'stock_id': code, 'date': f"{year}-12-31", 'open': end_p, 'high': end_p, 'low': end_p, 'close': end_p, 'volume': 0, 'market': 'TWSE'})
                
    # Process TPEx
    for year, year_data in tpex_results.items():
        if not year_data: continue
        for code, bounds in year_data.items():
            if code not in valid_tickers: continue
            start_p = float(bounds.get('start', 0.0))
            end_p = float(bounds.get('end', 0.0))
            if start_p > 0: all_records.append({'stock_id': code, 'date': f"{year}-01-02", 'open': start_p, 'high': start_p, 'low': start_p, 'close': start_p, 'volume': 0, 'market': 'TPEx'})
            if end_p > 0: all_records.append({'stock_id': code, 'date': f"{year}-12-31", 'open': end_p, 'high': end_p, 'low': end_p, 'close': end_p, 'volume': 0, 'market': 'TPEx'})
                
    if all_records:
        temp_df = pd.DataFrame(all_records)
        con.register('temp_df', temp_df)
        con.execute("INSERT OR IGNORE INTO daily_prices SELECT * FROM temp_df")
        con.unregister('temp_df')

    final_count = con.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
    final_stocks = con.execute("SELECT COUNT(DISTINCT stock_id) FROM daily_prices").fetchone()[0]
    print(f"✨ Market Boundary Restore Complete! Inserted {final_count} limits for {final_stocks} stocks.")
    con.close()

if __name__ == "__main__":
    asyncio.run(fetch_bounds())
