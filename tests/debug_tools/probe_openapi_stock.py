import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import httpx
import asyncio

async def probe_openapi():
    # Candidates
    urls = [
        "https://www.tpex.org.tw/openapi/v1/DailyQuotes",
        "https://www.tpex.org.tw/openapi/v1/StockDay",
        "https://www.tpex.org.tw/openapi/v1/TpexMainboardQuotes",
        "https://www.tpex.org.tw/openapi/swagger.json",
        "https://www.tpex.org.tw/openapi/v1/swagger.json"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    async with httpx.AsyncClient(verify=False) as client:
        for url in urls:
            print(f"Testing {url}...")
            try:
                resp = await client.get(url, headers=headers, timeout=5.0)
                print(f"Status: {resp.status_code}")
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        if 'paths' in data:
                            print("Paths Found:")
                            for p in list(data['paths'].keys())[:20]:
                                print(f"  {p}")
                        elif isinstance(data, list) and len(data) > 0:
                            print(f"Sample: {data[0]}")
                    except:
                        print("Not JSON")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(probe_openapi())
