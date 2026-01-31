import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import asyncio
from project_tw.crawler_tpex import TPEXCrawler

async def main():
    crawler = TPEXCrawler()
    # Mock universe to save time
    # 6669 (Wiwynn - but that's TWSE?), 3293 (IGS - TPEX), 8299 (Phison - TPEX)
    # 3293, 8299 are definitely TPEX.
    
    # Monkey patch _get_tpex_universe to return small list
    async def mock_universe(client):
        return ['3293', '8299', '8069']
    
    crawler._get_tpex_universe = mock_universe
    
    print("Testing fetch_ex_rights_history(2023)...")
    results = await crawler.fetch_ex_rights_history(2023)
    
    print("\nResults:")
    for code, data in results.items():
        print(f"{code}: {data}")

if __name__ == "__main__":
    asyncio.run(main())
