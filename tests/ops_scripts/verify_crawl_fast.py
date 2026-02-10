import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.services.market_data_service import MarketDataService
import asyncio

async def test_crawler_speed():
    service = MarketDataService()
    print("Testing crawler speed...")
    # ... logic ...
    
if __name__ == "__main__":
    asyncio.run(test_crawler_speed())
