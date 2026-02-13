
import logging
from pathlib import Path
from app.services.market_db import get_connection, DB_PATH
from app.services.market_data_provider import MarketDataProvider

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger("DuckDBStats")

def show_stats():
    if not DB_PATH.exists():
        logger.error(f"❌ Database not found at {DB_PATH}")
        return

    file_size_mb = DB_PATH.stat().st_size / (1024 * 1024)
    logger.info("=" * 40)
    logger.info("📊 DUCKDB MARKET DATABASE STATS")
    logger.info("-" * 40)
    logger.info(f"📁 Path: {DB_PATH}")
    logger.info(f"📁 Size: {file_size_mb:.2f} MB")
    
    stats = MarketDataProvider.get_stats()
    
    logger.info(f"📈 Price Rows:    {stats.get('price_rows', 0):,}")
    logger.info(f"💰 Dividend Rows: {stats.get('dividend_rows', 0):,}")
    logger.info(f"🏢 Stock Rows:    {stats.get('stock_rows', 0):,}")
    logger.info(f"📆 Date Range:   {stats.get('min_date', '?')} to {stats.get('max_date', '?')}")
    logger.info(f"📊 Distinct Stocks (Prices): {stats.get('distinct_stocks_prices', 0):,}")
    logger.info("=" * 40)

if __name__ == "__main__":
    show_stats()
