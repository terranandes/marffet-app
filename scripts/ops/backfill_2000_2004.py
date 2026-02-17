"""
Backfill 2000-2004 Data (Unadjusted)

Usage:
    uv run python scripts/ops/backfill_2000_2004.py [--test]

    --test: Only backfill 2330, 2317, 0050 to verify behavior.
"""
import sys
import os
import argparse
import logging

# Ensure app imports work
sys.path.insert(0, os.getcwd())

from app.services.market_data_service import backfill_all_stocks

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Test mode (limited tickers)")
    args = parser.parse_args()

    tickers = None
    if args.test:
        tickers = ["2330", "2317", "0050", "2454", "2303"]
        logger.info(f"TEST MODE: Backfilling only {tickers}")

    logger.info("Starting Backfill for 2000-01-01 to 2004-01-01...")
    
    result = backfill_all_stocks(
        period="max",
        start_date="2000-01-01",
        end_date="2004-01-01",
        overwrite=True, # to fill the gap
        include_warrants=False, # Skip 45,000+ warrants for speed
        chunk_size=1,
        tickers=tickers,
        progress_callback=lambda msg, pct: logger.info(f"[{pct}%] {msg}")
    )
    
    logger.info(f"Backfill Result: {result}")

if __name__ == "__main__":
    main()
