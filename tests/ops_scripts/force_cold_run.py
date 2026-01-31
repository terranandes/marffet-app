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

# Ensure app is in path
sys.path.insert(0, os.getcwd())

from app.services.crawler_service import CrawlerService

async def main():
    print("Triggering Full Cold Run via CrawlerService...")
    # This will now clear ALL cache due to our patch
    result = await CrawlerService.run_market_analysis(force_cold_run=True)
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
