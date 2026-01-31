import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import httpx
import asyncio

async def probe_cb():
    candidate_url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
    
    candidates = [
        # Candidate 8: Stock Quote with Specific Code
        {
            "url": candidate_url, 
            "params": {"l": "zh-tw", "d": "112/06/01", "stkno": "65331", "o": "json"}, 
            "desc": "Stk Quote (stkno=65331)"
        },
        # Candidate 9: Stock Quote with 'sect=Bond'?
         {
            "url": candidate_url, 
            "params": {"l": "zh-tw", "d": "112/06/01", "sect": "Bond", "o": "json"}, 
            "desc": "Stk Quote (sect=Bond)"
        }
    ]
    
    headers = {"User-Agent": "Mozilla/5.0"}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for c in candidates:
            try:
                print(f"--- Probing {c['desc']} ---")
                print(f"URL: {c['url']}")
                resp = await client.get(c['url'], params=c.get('params'), headers=headers, timeout=10.0)
                print(f"Status: {resp.status_code}")
                
                try:
                    data = resp.json()
                    keys = list(data.keys())
                    print(f"JSON Found! Keys: {keys}")
                    if 'aaData' in data:
                        print(f"Sample Item: {data['aaData'][0]}")
                except:
                    print(f"Not JSON. Content Sample: {resp.text[:300]}")
                    
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(probe_cb())
