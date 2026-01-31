import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import httpx
import asyncio

async def debug_bond_fetch():
    base_url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw"
    }
    roc_date = "114/06/02" # Future date? No. 2025-06-02 is future.
    # Today is 2025-12-10 -> 114/12/10.
    # Let's try a valid recent date. 2025-06-02 was Monday.
    # Wait, today is 2025-12-10.
    # Let's try 114/12/10? No, 114 is 2025.
    roc_date = "114/12/09" # Yesterday
    
    # Test Specific Code
    params_specific = { "l": "zh-tw", "d": roc_date, "o": "json", "stkno": "65331" }
    
    print(f"Fetching Specific Code 65331 for {roc_date}...")
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(base_url, params=params_specific, headers=headers)
            print(f"Status: {resp.status_code}")
            data = resp.json()
            
            aaData = data.get('aaData', [])
            tables = data.get('tables', [])
            
            if aaData:
                print(f"aaData Count: {len(aaData)}")
                print(f"Row 0: {aaData[0]}")
            
            if tables:
                 print(f"Tables Count: {len(tables)}")
                 for t in tables:
                     print(f"Title: {t.get('title')}")
                     if t.get('data'):
                         print(f"Row 0: {t['data'][0]}")

            
        except Exception as e:
            print(f"Error: {e}")

    params_cb = { "l": "zh-tw", "d": roc_date, "o": "json", "sect": "Bond" }
    
    print(f"Fetching Bond Data for {roc_date}...")
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(base_url, params=params_cb, headers=headers)
            print(f"Status: {resp.status_code}")
            data = resp.json()
            
            aaData = data.get('aaData', [])
            tables = data.get('tables', [])
            
            print(f"aaData Count: {len(aaData)}")
            print(f"Tables Count: {len(tables)}")
            
            if aaData:
                print("First 3 items in aaData:")
                for i in range(min(3, len(aaData))):
                    print(aaData[i])
                    
                # Check for 65331 specifically
                found = False
                for row in aaData:
                    if "65331" in str(row):
                         print(f"FOUND 65331 in aaData: {row}")
                         found = True
                         break
                if not found:
                    print("65331 NOT found in aaData.")
                    
            if tables:
                print("Checking tables...")
                for t in tables:
                     print(f"Table Title: {t.get('title')}")
                     rows = t.get('data', [])
                     print(f"Rows: {len(rows)}")
                     if rows:
                         print(f"Sample Row: {rows[0]}")
                         
                     for row in rows:
                        if "65331" in str(row):
                             print(f"FOUND 65331 in Table: {row}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_bond_fetch())
