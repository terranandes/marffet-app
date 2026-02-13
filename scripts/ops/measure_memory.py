
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

def measure_cache_size():
    print(f"Empty RAM: {get_memory_usage():.2f} MB")
    
    # Force load (Simulate Cloud Mode: 2 years - SAFER)
    print("Loading MarketCache (2025-2026)...")
    
    # Manually simulate the filter since API doesn't exist yet
    MarketCache.START_YEAR = 2025 
    cache = MarketCache.get_prices_db(force_reload=True, incremental=False)
    
    gc.collect()
    mem = get_memory_usage()
    print(f"Full Cache RAM: {mem:.2f} MB")
    
    # Count ticks
    total_ticks = 0
    for y in cache:
        for m in cache[y]:
            total_ticks += len(cache[y][m])
    print(f"Total Tickers Loaded: {total_ticks}")

if __name__ == "__main__":
    # Mocking path if needed, but MarketCache uses relative path
    measure_cache_size()
