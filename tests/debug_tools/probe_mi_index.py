import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import httpx
import asyncio

async def probe():
    url = "https://www.twse.com.tw/exchangeReport/MI_INDEX"
    stock = "6238" # Flexium (TWSE)
    # Check 3174 too?
    date = "20241211"
    
    types = ["ALLBUT0999"]
    
    async with httpx.AsyncClient() as client:
        for t in types:
            print(f"--- Probing type={t} ---")
            params = {"response": "json", "date": date, "type": t}
            try:
                resp = await client.get(url, params=params, timeout=10)
                data = resp.json()
                if data.get('stat') != 'OK':
                    print("  Stat:", data.get('stat'))
                    continue
                
                found = False
                tables = data.get('tables', [])
                # Also check data8/data9
                raw_rows = []
                for tbl in tables:
                     raw_rows.extend(tbl.get('data', []))
                
                # Check data9 fallback
                if not raw_rows:
                    raw_rows = data.get('data9', []) or data.get('data8', [])
                
                print(f"  Total Rows: {len(raw_rows)}")
                if len(raw_rows) > 0:
                    print(f"  Sample Code: '{raw_rows[0][0]}'")
                
                for r in raw_rows:
                    if len(r) > 0:
                        code = str(r[0]).strip()
                        if stock in code: # Fuzzy
                            print(f"  FOUND {stock} (Fuzzy): '{r[0]}' -> '{code}'")
                            found = True
                            # Don't break, maybe multiple
                
                if not found:
                    print(f"  NOT FOUND {stock}")
            except Exception as e:
                print(f"  Error: {e}")
            
            await asyncio.sleep(2)

asyncio.run(probe())
