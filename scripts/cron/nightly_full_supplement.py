#!/usr/bin/env python3
"""
Nightly Full Universe Supplement — ALL stocks, period=2d

Purpose: Keeps DuckDB current with T-0 close data for all 1,629 stocks.
Schedule: Nightly at 22:00 HKT (after TWSE close at 13:30)

Usage:
    uv run python scripts/cron/nightly_full_supplement.py

Design:
    - period=2d returns last 2 trading days (1-day safety buffer if cron misses a night)
    - Overwrites existing data (upsert) so no duplicates
    - Targets ALL stocks in DuckDB, not just portfolio-held ones
    - SIM_CACHE is invalidated automatically on next API request (TTL-based)
"""

import sys
import time
import logging
from pathlib import Path

# Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("NightlyFull")

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    logger.info("=" * 60)
    logger.info("🌙 NIGHTLY FULL UNIVERSE SUPPLEMENT (ALL → DuckDB)")
    logger.info("=" * 60)

    t0 = time.time()

    # 1. Get all stock IDs from DuckDB
    from app.services.market_data_provider import MarketDataProvider
    stock_ids = MarketDataProvider.get_stock_list()
    logger.info(f"📊 Universe: {len(stock_ids)} stocks")

    if not stock_ids:
        logger.error("❌ No stocks found in DuckDB. Aborting.")
        sys.exit(1)

    # 2. Run backfill with period=2d (today + 1-day safety buffer)
    # yfinance period=2d returns the last 2 trading days,
    # so if cron misses one night, yesterday's data is still captured.
    from app.services.market_data_service import backfill_all_stocks
    
    result = backfill_all_stocks(
        period="2d",
        overwrite=True,
        tickers=stock_ids
    )

    t1 = time.time()
    elapsed = t1 - t0

    if result.get("status") == "error":
        logger.error(f"❌ Backfill failed: {result.get('message')}")
        sys.exit(1)

    logger.info(f"✅ Full universe supplement completed in {elapsed:.0f}s")
    logger.info(f"   Stocks: {len(stock_ids)}")
    logger.info(f"   Period: 2d (today + safety buffer)")

    # 3. Warm the latest price cache
    logger.info("🔥 Warming latest price cache...")
    MarketDataProvider.warm_latest_cache()
    logger.info("✅ Cache warmed. Mars tab will use fresh data on next load.")

    logger.info("=" * 60)
    logger.info("🎉 NIGHTLY SUPPLEMENT DONE")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
