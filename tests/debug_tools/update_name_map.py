import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import httpx
import pandas as pd
import asyncio

async def fetch_names():
    name_map = {}
    
    async with httpx.AsyncClient(verify=False) as client:
        # 1. TWSE (BWIBBU_d - All Securities)
        # OR MI_INDEX? MI_INDEX type=ALLBUT0999 has names.
        print("Fetching TWSE Names...")
        try:
            url = "https://www.twse.com.tw/exchangeReport/MI_INDEX"
            params = {"response": "json", "type": "ALLBUT0999", "date": "20241213"} # Use recent Friday
            resp = await client.get(url, params=params, timeout=15)
            data = resp.json()
            if data['stat'] == 'OK':
                # find table with code/name
                tables = data.get('tables', [])
                # Usually table 8 or 9
                raw = []
                for t in tables:
                     if '證券代號' in t['fields']:
                         raw = t['data']
                         break
                for r in raw:
                    code = r[0]
                    name = r[1]
                    name_map[code] = name
            else:
                print("TWSE Stat:", data['stat'])
        except Exception as e:
            print(f"TWSE Error: {e}")

        # 2. TPEx (stk_quote_result)
        print("Fetching TPEx Names...")
        try:
            url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
            params = {"l": "en-us", "d": "113/12/13", "se": "EW"} # Equities
            resp = await client.get(url, params=params, timeout=15)
            data = resp.json()
            if 'aaData' in data:
                for r in data['aaData']:
                    code = r[0]
                    name = r[1]
                    name_map[code] = name
        except Exception as e:
            print(f"TPEx Error: {e}")
            
        # 3. Handle Special Cases (ETFs?)
        # TPEx ETFs are under different param? se=EW is Equity. 
        # Need se=AL (All)? Or separate call.
        # Try fetching TPEx ALL
        try:
            print("Fetching TPEx ETFs/Others...")
            params['se'] = 'AL' # All
            resp = await client.get(url, params=params, timeout=15)
            data = resp.json()
            if 'aaData' in data:
                for r in data['aaData']:
                    code = r[0]
                    name = r[1]
                    name_map[code] = name
        except Exception:
            pass

    print(f"Collected {len(name_map)} names.")
    
    # Save to CSV
    df = pd.DataFrame(list(name_map.items()), columns=['code', 'name'])
    df.to_csv('project_tw/stock_list.csv', index=False)
    print("Saved to project_tw/stock_list.csv")

if __name__ == "__main__":
    asyncio.run(fetch_names())
