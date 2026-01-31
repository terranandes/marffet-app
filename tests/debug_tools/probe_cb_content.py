import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import httpx
import asyncio

async def probe_cb_content():
    url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
    
    # Test 1: sect=Bond (Bulk Fetch?)
    params_bulk = {"l": "zh-tw", "d": "112/06/01", "sect": "Bond", "o": "json"}
    
    # Test 2: stkno=65331 (Specific Fetch)
    params_specific = {"l": "zh-tw", "d": "112/06/01", "stkno": "65331", "o": "json"}
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    async with httpx.AsyncClient() as client:
        try:
            print("--- Fetching sect=Bond ---")
            resp = await client.get(url, params=params_bulk, headers=headers)
            data = resp.json()
            # print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
            ct = 0
            if 'aaData' in data:
                ct = len(data['aaData'])
                print(f"aaData Count: {ct}")
            if 'tables' in data:
                print(f"Tables Count: {len(data['tables'])}")
                if len(data['tables']) > 0:
                     print(f"Table 0 Rows: {len(data['tables'][0]['data'])}")
                     print(f"Sample Row: {data['tables'][0]['data'][0]}")

            print("\n--- Fetching stkno=65331 ---")
            resp = await client.get(url, params=params_specific, headers=headers)
            data = resp.json()
            if 'tables' in data and len(data['tables']) > 0:
                print(f"Data for 65331: {data['tables'][0]['data']}")
            elif 'aaData' in data and len(data['aaData']) > 0:
                print(f"Data for 65331: {data['aaData']}")
            else:
                print("No data in tables/aaData for 65331")
                print(f"Keys: {data.keys()}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(probe_cb_content())
