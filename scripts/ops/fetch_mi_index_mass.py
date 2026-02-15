import asyncio
import httpx
import json
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Ensure we can import app
sys.path.append(os.getcwd())
from app.services.market_db import get_connection

class MIIndexMassFetcher:
    def __init__(self, cache_dir="data/raw/mi_index"):
        self.base_url = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.semaphore = asyncio.Semaphore(1) 
        self.db_path = "data/market.duckdb"

    async def fetch_date(self, client, date_str):
        cache_file = self.cache_dir / f"MI_INDEX_{date_str}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass

        params = {"response": "json", "date": date_str, "type": "ALLBUT0999"}
        async with self.semaphore:
            for attempt in range(3):
                try:
                    # Adaptive delay for mass fetch
                    delay = 3.5 + (attempt * 10.0)
                    await asyncio.sleep(delay)
                    
                    resp = await client.get(self.base_url, params=params, timeout=20.0)
                    if resp.status_code == 200:
                        data = resp.json()
                        if data and data.get('stat') == 'OK':
                            with open(cache_file, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False)
                            return data
                        elif "查詢頻率過高" in str(data):
                            print(f"  🛑 Rate limited at {date_str}. Sleeping 60s...", flush=True)
                            await asyncio.sleep(60.0)
                        else:
                            # Likely weekend or holiday
                            return {"stat": "EMPTY"}
                    elif resp.status_code == 403:
                        print(f"  🚫 403 Forbidden at {date_str}. Sleeping 300s...", flush=True)
                        await asyncio.sleep(300.0)
                except Exception as e:
                    print(f"  ❌ Error for {date_str}: {e}", flush=True)
            return None

    def parse_mi_index(self, data, date_str):
        if not data or data.get('stat') != 'OK':
            return []
            
        quotes_table = None
        for t in data.get('tables', []):
            if '證券代號' in str(t.get('fields', [])):
                quotes_table = t
                break
        
        if not quotes_table:
            return []

        rows = quotes_table['data']
        batch = []
        for r in rows:
            try:
                sid = r[0].strip()
                if len(sid) > 4 and not (sid.isdigit() or sid.endswith('KY')): continue # Filter weird tickers
                
                # MI_INDEX Fields: [0:Id, 1:Name, 2:Vol, 3:Counts, 4:Amount, 5:Open, 6:High, 7:Low, 8:Close]
                vol = int(r[2].replace(',', ''))
                op = float(r[5].replace(',', ''))
                hi = float(r[6].replace(',', ''))
                lo = float(r[7].replace(',', ''))
                cl = float(r[8].replace(',', ''))
                
                # AD date from YYYYMMDD
                dt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                batch.append((sid, dt, op, hi, lo, cl, vol, 'TWSE'))
            except:
                pass
        return batch

    async def run_restoration(self, start_date_str="20060101", end_date_str=None):
        if not end_date_str:
            end_date_str = datetime.now().strftime("%Y%m%d")
            
        start_dt = datetime.strptime(start_date_str, "%Y%m%d")
        end_dt = datetime.strptime(end_date_str, "%Y%m%d")
        
        print(f"🚀 Mass Restoring Nominal Prices: {start_date_str} to {end_date_str}", flush=True)
        
        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
            current_dt = start_dt
            cumulative_batch = []
            
            while current_dt <= end_dt:
                ds = current_dt.strftime("%Y%m%d")
                data = await self.fetch_date(client, ds)
                
                if data and data.get('stat') == 'OK':
                    batch = self.parse_mi_index(data, ds)
                    cumulative_batch.extend(batch)
                    print(f"  ✅ {ds}: {len(batch)} stocks found.", flush=True)
                
                # Periodically flush to DB to keep memory low
                if len(cumulative_batch) > 10000:
                    self.flush_to_db(cumulative_batch)
                    cumulative_batch = []
                
                current_dt += timedelta(days=1)
                
            if cumulative_batch:
                self.flush_to_db(cumulative_batch)
        
        print("🏁 Mass restoration complete.", flush=True)

    def flush_to_db(self, batch):
        print(f"📥 Flushing {len(batch)} records to DuckDB...", flush=True)
        conn = get_connection()
        try:
            # We use INSERT OR REPLACE logic or just append. 
            # Since we want a "Nominal Reset", we might want to prioritize these over existing records.
            # For now, we use a temporary table and then swap/merge.
            conn.execute("CREATE TEMP TABLE IF NOT EXISTS temp_nominal AS SELECT * FROM daily_prices LIMIT 0")
            conn.executemany("""
                INSERT INTO temp_nominal (stock_id, date, open, high, low, close, volume, market)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, batch)
            
            # Merge into main table
            conn.execute("""
                INSERT INTO daily_prices 
                SELECT * FROM temp_nominal 
                ON CONFLICT (stock_id, date) DO UPDATE SET 
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume,
                    market = 'TWSE_NOMINAL'
            """)
            conn.execute("DROP TABLE temp_nominal")
            print("  💾 Commit successful.", flush=True)
        except Exception as e:
            print(f"  ❌ DB Error: {e}", flush=True)
        finally:
            conn.close()

if __name__ == "__main__":
    fetcher = MIIndexMassFetcher()
    # Check if a start year is provided
    start_date = sys.argv[1] if len(sys.argv) > 1 else "20060101"
    asyncio.run(fetcher.run_restoration(start_date))
