
import os
import sys
import resource
import gc
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.market_cache import MarketCache

def get_memory_usage():
    # resource.getrusage returns in KB on Linux
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # MB

def setup_dummy_db():
    db_path = Path("data/portfolio.db")
    if not db_path.exists():
        print("Creating dummy portfolio.db for benchmark...")
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS race_cache (stock_id TEXT, month TEXT, close_price REAL, PRIMARY KEY (stock_id, month))")
            # Fill 2006-2024 with dummy data for 2330
            data = []
            for y in range(2006, 2025):
                for m in range(1, 13):
                    data.append(('2330', f"{y}-{m:02d}", 100.0 + y - 2000))
            conn.executemany("INSERT OR REPLACE INTO race_cache VALUES (?, ?, ?)", data)

def benchmark_fetch():
    setup_dummy_db()
    print(f"Empty RAM: {get_memory_usage():.2f} MB")
    
    # 1. Load RAM Cache (Small)
    print("Loading RAM Cache (2025-2026)...")
    MarketCache.START_YEAR = 2025
    MarketCache.get_prices_db(force_reload=True, incremental=False)
    print(f"RAM Cache Loaded: {get_memory_usage():.2f} MB")
    
    # 2. Fetch Deep History for TSMC (2330)
    print("Fetching TSMC History (2006-2026) via Hybrid Strategy...")
    history = MarketCache.get_strategy_history("2330", start_year=2006)
    
    print(f"Memory Post-Fetch: {get_memory_usage():.2f} MB")
    print(f"History Length: {len(history)} records")
    if history:
        print(f"First: {history[0]}")
        print(f"Last: {history[-1]}")

if __name__ == "__main__":
    benchmark_fetch()
