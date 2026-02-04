
import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Mock Environment
os.environ["SECRET_KEY"] = "debug"

import asyncio
from app.main import get_simulation_detail
from app.services.market_cache import MarketCache
from app.portfolio_db import init_db

def test_6415():
    print("--- Initializing DB & Cache ---")
    # We need to pre-warm cache because get_simulation_detail relies on it or falls back to DB?
    # Actually get_simulation_detail logic:
    # 1. Check SIM_CACHE
    # 2. MarketCache.get_stock_history_fast(stock_id)
    # 3. ROICalculator...
    
    # We must initialize MarketCache to ensure it has data
    MarketCache.get_prices_db(force_reload=True)
    
    stock_id = "6415"
    print(f"--- Running Simulation for {stock_id} ---")
    
    try:
        result = get_simulation_detail(
            stock_id=stock_id,
            start_year=2006, 
            principal=1000000, 
            contribution=60000
        )
        print("--- Result ---")
        print(result)
    except Exception as e:
        print("--- CRASH DETECTED ---")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_6415()
