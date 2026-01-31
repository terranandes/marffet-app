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
    # Base: https://www.tpex.org.tw/openapi/v1
    # Candidates based on search hints
    candidates = [
        # 1. Exact hint
        {"url": "https://www.tpex.org.tw/openapi/v1/bond_cb_daily", "desc": "Bond CB Daily"},
        
        # 2. Maybe under 'bond'?
        {"url": "https://www.tpex.org.tw/openapi/v1/bond/cb_daily", "desc": "Bond/CB Daily"},
        
        # 3. List Bonds?
        {"url": "https://www.tpex.org.tw/openapi/v1/bond/list", "desc": "Bond List"},
    ]
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    async with httpx.AsyncClient(verify=False) as client: # Disable SSL verify for test
        for c in candidates:
            try:
                print(f"--- Probing {c['desc']} ---")
                resp = await client.get(c['url'], headers=headers, timeout=10.0)
                print(f"Status: {resp.status_code}")
                # print(f"Content: {resp.text[:200]}")
                try:
                    data = resp.json()
                    print(f"JSON Found! Keys type: {type(data)}")
                    if isinstance(data, list) and len(data) > 0:
                        print(f"Sample: {data[0]}")
                except:
                    print("Not JSON.")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(probe_openapi())
