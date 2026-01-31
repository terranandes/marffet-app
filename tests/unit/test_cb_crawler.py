import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import asyncio
import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Mock env if needed
os.environ["IS_PRODUCTION"] = "False"

from app.project_tw.crawler_cb import CBCrawler

async def main():
    crawler = CBCrawler()
    cb_code = "65331"
    stock_code = "6533"
    
    print(f"Testing Crawler for CB: {cb_code}, Stock: {stock_code}")
    cb_price, st_price, success = await crawler.get_market_data(cb_code, stock_code)
    
    print(f"Result: CB Price={cb_price}, Stock Price={st_price}, Success={success}")

if __name__ == "__main__":
    asyncio.run(main())