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
