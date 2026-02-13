import resource
import logging
import requests
import time
from app.services.market_data_provider import MarketDataProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_ram_usage():
    """
    Verify steady state RAM < 200MB.
    Task 10.5 in PRD.
    """
    logger.info("Measuring RAM usage...")
    
    # 1. Base RAM
    usage_start = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 # MB
    logger.info(f"Initial RAM usage: {usage_start:.2f} MB")
    
    # 2. Warm cache
    logger.info("Warming latest price cache...")
    try:
        MarketDataProvider.warm_latest_cache()
    except Exception as e:
        logger.warning(f"Could not warm cache (is DB locked?): {e}")
    
    # 3. Steady state
    usage_end = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 # MB
    logger.info(f"Steady state RAM usage: {usage_end:.2f} MB")
    
    if usage_end < 200:
        logger.info("✅ RAM usage within criteria (< 200MB).")
    else:
        logger.warning(f"⚠️ RAM usage {usage_end:.2f} MB exceeds 200MB.")

if __name__ == "__main__":
    verify_ram_usage()
