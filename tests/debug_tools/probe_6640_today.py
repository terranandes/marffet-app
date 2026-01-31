import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import httpx
import asyncio

async def check_today():
    url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
    # No date param = Today
    params = {"l": "zh-tw", "o": "json"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw"
    }
    
    async with httpx.AsyncClient() as client:
        print("Fetching TPEx Today...")
        resp = await client.get(url, params=params, headers=headers)
        data = resp.json()
        
        tables = data.get('tables', [])
        found = False
        for t in tables:
            rows = t.get('data', [])
            for r in rows:
                if r[0] == '6640':
                    print(f"Found 6640 Today: {r}")
                    found = True
        
        if not found:
            print("6640 Not found Today.")

if __name__ == "__main__":
    asyncio.run(check_today())
