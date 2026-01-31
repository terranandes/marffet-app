import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import httpx
import asyncio

async def debug_tpex():
    url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
    
    # Target: 2024/01/05 (Friday)
    # ROC: 113/01/05
    target_date = "113/01/05"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw"
    }
    
    tests = [
        {"desc": "Market Wide (d=113/01/05)", "params": {"l": "zh-tw", "d": "113/01/05", "o": "json"}},
        {"desc": "Single 6640 (d=113/01/05)", "params": {"l": "zh-tw", "d": "113/01/05", "stkno": "6640", "o": "json"}}
    ]
    
    for t in tests:
        print(f"\n--- Testing {t['desc']} ---")
        await asyncio.sleep(2.0)
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, params=t['params'], headers=headers, timeout=10.0)
                if resp.status_code != 200:
                    print(f"Status: {resp.status_code}")
                    continue
                
                data = resp.json()
                print(f"ReportDate: {data.get('reportDate')}")
                
                # Check for 6640 in aaData or tables
                found_price = None
                
                # Check aaData
                aaData = data.get('aaData', [])
                for r in aaData:
                    if len(r) > 0 and (r[0] == '6640' or t['params'].get('stkno') == '6640'):
                       # If StkNo queried, row might not have code in col 0? 
                       # Usually for single stock, it returns list of *days* for that month?
                       # Or list of trade info for that day?
                       print(f"  Row: {r}")
                       # If Single Stock Month Query, standard TPEx single format is Daily lines.
                       # But we queried ONE day `d=113/01/05`.
                       # Let's see output structure.
                       pass

                # Check Tables
                tables = data.get('tables', [])
                for tbl in tables:
                     rows = tbl.get('data', [])
                     for r in rows:
                        if len(r) > 0 and r[0] == '6640':
                            found_price = r[2]
                            print(f"  6640 Price (Table): {found_price}")
                
                if not found_price and not aaData:
                    print("  No 6640 data found.")
                    
            except Exception as e:
                print(f"Err {t['desc']}: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(debug_tpex())
