import asyncio
import httpx
import os
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

# Ensure we can import app
sys.path.append(os.getcwd())

from app.services.market_db import get_connection

class NominalRestorer:
    def __init__(self, raw_cache_dir="data/raw/stock_day"):
        self.base_url = "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY"
        self.cache_dir = Path(raw_cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.semaphore = asyncio.Semaphore(1) # STRICT: 1 at a time for TWSE
        
    async def fetch_month(self, client, code, date_str):
        # 1. Check Cache First
        year_month = date_str[:6] # YYYYMM
        cache_file = self.cache_dir / f"{code}_{year_month}.json"
        
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                try: 
                    return json.load(f)
                except: pass

        # 2. Fetch if not in cache
        params = {
            "response": "json",
            "stockNo": code,
            "date": date_str
        }
        
        async with self.semaphore:
            for attempt in range(3):
                try:
                    # Adaptive delay: TWSE is very sensitive. 
                    # 2-5 seconds between requests is safer for long batches.
                    delay = 3.0 + (attempt * 10.0) 
                    await asyncio.sleep(delay)
                    
                    resp = await client.get(self.base_url, params=params, timeout=20.0)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        if data and data.get('stat') == 'OK':
                            with open(cache_file, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False)
                            return data
                        elif "查詢頻率過高" in str(data):
                            print(f"  🛑 TWSE Rate Limit Hit (頻率過高). Sleeping 30s...")
                            await asyncio.sleep(30.0)
                        else:
                            print(f"  ⚠️ {code} {year_month} Stat: {data.get('stat')}")
                            return None
                    elif resp.status_code == 403:
                        print("  🚫 403 Forbidden. TWSE has blocked this IP temporarily. Sleeping 60s...")
                        await asyncio.sleep(60.0)
                except Exception as e:
                    print(f"  ❌ Attempt {attempt+1} Error for {code} {date_str}: {e}")
        return None

    def _taiwan_to_ad(self, date_str):
        parts = date_str.split('/')
        y = int(parts[0]) + 1911
        return f"{y}-{parts[1]}-{parts[2]}"

    async def restore_stock(self, code, start_year=2006, end_year=2025):
        print(f"\n🔄 Restoring Nominal Prices for {code} ({start_year}-{end_year})...")
        
        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
            all_rows = []
            for year in range(start_year, end_year + 1):
                # Process months sequentially to avoid massive concurrent failures
                for month in range(1, 13):
                    if year == datetime.now().year and month > datetime.now().month: continue
                    
                    date_str = f"{year}{month:02d}01"
                    data = await self.fetch_month(client, code, date_str)
                    
                    if data and 'data' in data:
                        for row in data['data']:
                            try:
                                dt = self._taiwan_to_ad(row[0])
                                vol = int(row[1].replace(',', ''))
                                op = float(row[3].replace(',', ''))
                                hi = float(row[4].replace(',', ''))
                                lo = float(row[5].replace(',', ''))
                                cl = float(row[6].replace(',', ''))
                                all_rows.append((code, dt, op, hi, lo, cl, vol, 'TWSE'))
                            except: pass
                
                print(f"  ✅ Year {year} complete ({len(all_rows)} total rows)")

            if all_rows:
                conn = get_connection()
                # Use a transaction for safety
                conn.execute("BEGIN TRANSACTION")
                try:
                    conn.execute("DELETE FROM daily_prices WHERE stock_id = ?", [code])
                    conn.executemany("""
                        INSERT INTO daily_prices (stock_id, date, open, high, low, close, volume, market)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, all_rows)
                    conn.execute("COMMIT")
                    print(f"✅ Success: {code} is now NOMINAL ({len(all_rows)} rows).")
                except Exception as e:
                    conn.execute("ROLLBACK")
                    print(f"❌ DB Error for {code}: {e}")
                finally:
                    conn.close()

if __name__ == "__main__":
    import json
    
    # Batch Support
    if len(sys.argv) < 2:
        print("Usage: python restore_nominal_prices.py <stock_id|--file> [path_to_json] [start_year]")
        sys.exit(1)
        
    mode = sys.argv[1]
    restorer = NominalRestorer()
    
    if mode == "--file":
        report_path = sys.argv[2]
        start_yr = int(sys.argv[3]) if len(sys.argv) > 3 else 2006
        with open(report_path, 'r') as f:
            report = json.load(f)
        outliers = report.get('cagr_outliers', [])
        codes = [o['stock_id'] for o in outliers[:20]] # Process 20 at a time
        print(f"🚀 Batch restoring {len(codes)} stocks...")
        for c in codes:
            asyncio.run(restorer.restore_stock(c, start_yr))
    else:
        code = sys.argv[1]
        start = int(sys.argv[2]) if len(sys.argv) > 2 else 2006
        asyncio.run(restorer.restore_stock(code, start))
