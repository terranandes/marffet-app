import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import asyncio
from project_tw.crawler_tpex import TPEXCrawler

async def verify():
    crawler = TPEXCrawler()
    print("Fetching TPEx 2024...")
    data = await crawler.fetch_market_prices_batch([2024])
    
    codes = ['6640', '006201']
    for c in codes:
        if 2024 in data and c in data[2024]:
            p = data[2024][c]
            print(f"{c} 2024: Start={p['start']}, End={p['end']}")

if __name__ == "__main__":
    asyncio.run(verify())
