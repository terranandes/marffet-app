import asyncio
import httpx
import json
import os
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

# Ensure we can import app
sys.path.append(os.getcwd())
from app.services.market_db import get_connection

class YearlyNominalSnapshot:
    def __init__(self, data_dir="data/raw/yearly_nominal"):
        self.base_url = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.semaphore = asyncio.Semaphore(1)

    async def fetch_mi_index(self, client, date_str):
        cache_file = self.data_dir / f"MI_INDEX_{date_str}.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        params = {"response": "json", "date": date_str, "type": "ALLBUT0999"}
        async with self.semaphore:
            try:
                print(f"  🌐 Fetching MI_INDEX for {date_str}...")
                await asyncio.sleep(4.0) # Very safe delay
                resp = await client.get(self.base_url, params=params, timeout=20.0)
                if resp.status_code == 200:
                    data = resp.json()
                    if data and data.get('stat') == 'OK':
                        with open(cache_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False)
                        return data
                return None
            except Exception as e:
                print(f"Error for {date_str}: {e}")
                return None

    async def get_first_trading_day(self, client, year, month=1):
        # Try days 1 to 15 until 'OK'
        for d in range(1, 16):
            date_str = f"{year}{month:02d}{d:02d}"
            data = await self.fetch_mi_index(client, date_str)
            if data and data.get('stat') == 'OK':
                return data
        return None

    async def run_snapshot(self, start_year=2006, end_year=2025):
        print(f"🚀 Starting Yearly Nominal Snapshot ({start_year}-{end_year})...")
        
        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
            all_historical_data = {}
            for year in range(start_year, end_year + 1):
                data = await self.get_first_trading_day(client, year)
                if data:
                    print(f"  ✅ Year {year} checkpoint found.")
                    # MI_INDEX tables[8] or tables[9] usually contains the daily quotes
                    # We need to find the table with the stock prices.
                    quotes_table = None
                    for t in data.get('tables', []):
                        if '證券代號' in str(t.get('fields', [])):
                            quotes_table = t
                            break
                    
                    if quotes_table:
                        # Map: {stock_id: close}
                        rows = quotes_table['data']
                        year_prices = {}
                        for r in rows:
                            try:
                                sid = r[0].strip()
                                # Close is usually index 8
                                close = float(r[8].replace(',', ''))
                                year_prices[sid] = close
                            except: pass
                        all_historical_data[year] = year_prices
            
            # Save final results
            with open('data/yearly_nominal_prices.json', 'w') as f:
                json.dump(all_historical_data, f)
            print("🏁 Yearly snapshot complete. Saved to data/yearly_nominal_prices.json")

if __name__ == "__main__":
    snapshot = YearlyNominalSnapshot()
    asyncio.run(snapshot.run_snapshot())
