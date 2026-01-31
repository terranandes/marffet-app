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

async def fetch_twse_stock_list():
    print("Fetching stock list from TWSE...")
    url = "https://www.twse.com.tw/rwd/zh/afterTrading/BWIBBU_d?response=json"
    
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            data = r.json()
        
        if data.get('stat') != 'OK':
            print("Error fetching data")
            return

        rows = []
        for item in data['data']:
            # Item: [Code, Name, PE, DivYield, PB]
            code = item[0]
            name = item[1]
            rows.append({'code': code, 'name': name})
            
        df = pd.DataFrame(rows)
        print(f"Fetched {len(df)} stocks.")
        print(df.head())
        
        df.to_csv("project_tw/stock_list.csv", index=False)
        print("Saved to project_tw/stock_list.csv")
        
    except Exception as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(fetch_twse_stock_list())
