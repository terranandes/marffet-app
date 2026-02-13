
"""
Targeted Stock Data Patcher (DuckDB version)
Downloads specific stock(s) via yfinance and patches them into DuckDB.
Usage:
    uv run python scripts/ops/patch_stock_data.py --stocks 2330 2317 2454
"""
import argparse
import logging
import time
from typing import List
from app.services.market_data_service import backfill_all_stocks

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("PatchStock")

def main():
    parser = argparse.ArgumentParser(description="Patch specific stock data into DuckDB")
    parser.add_argument("--stocks", nargs="+", required=True, help="Stock codes to patch (e.g., 2330 2317)")
    parser.add_argument("--start-year", type=int, default=2000, help="Start year (unused, uses yfinance period='max' for consistency)")
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("🔧 TARGETED STOCK DATA PATCHER (DUCKDB)")
    logger.info(f"   Stocks: {', '.join(args.stocks)}")
    logger.info("=" * 50)

    start_time = time.time()
    
    # We use the existing backfill_all_stocks function but pass specific tickers.
    # This ensures consistency with the main writer logic.
    result = backfill_all_stocks(
        period="max", 
        overwrite=True, 
        tickers=args.stocks,
        progress_callback=lambda msg, pct: logger.info(f"[{pct:>3}%] {msg}")
    )

    elapsed = time.time() - start_time
    logger.info("=" * 50)
    if result.get("status") == "success" or "Market data sync complete" in str(result):
        logger.info(f"✨ PATCH COMPLETE in {elapsed:.1f}s")
    else:
        logger.error(f"❌ PATCH FAILED: {result.get('message', 'Unknown error')}")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
