import sqlite3
import subprocess
import os
import sys
from pathlib import Path
import logging

# Setup Logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("SupplementPrices")

# Load Martian App Path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.market_data_service import backfill_all_stocks

# Config
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "app" / "portfolio.db"
# If on Zeabur, it might be in /data/portfolio.db
ZEABUR_DB = Path("/data/portfolio.db")
if ZEABUR_DB.exists():
    DB_PATH = ZEABUR_DB

CRAWLER_SCRIPT = PROJECT_ROOT / "scripts" / "ops" / "crawl_fast.py"

# Essential ETFs and stocks to always keep fresh
TOP_UNIVERSE = [
    "0050", "0056", "006208", "00878", "00713", "00919", "00929", # Top ETFs
    "2330", "2317", "2454", "2308", "2881", "2882", # Market Cap Leaders
    "00940", "00939" # Newer popular ETFs
]

def get_active_tickers():
    """Fetch all unique stock_ids from group_targets table."""
    if not DB_PATH.exists():
        logger.warning(f"⚠️ Database not found at {DB_PATH}. Using TOP_UNIVERSE only.")
        return set(TOP_UNIVERSE)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Query unique stock ids from group_targets
        cursor.execute("SELECT DISTINCT stock_id FROM group_targets")
        rows = cursor.fetchall()
        tickers = {row[0] for row in rows if row[0] and len(row[0]) >= 4}
        conn.close()
        logger.info(f"✅ Found {len(tickers)} active stocks in portfolios.")
        
        # Merge with top universe
        final_set = tickers.union(set(TOP_UNIVERSE))
        return final_set
    except Exception as e:
        logger.error(f"❌ Error querying database: {e}")
        return set(TOP_UNIVERSE)

def run_supplemental_backfill(tickers):
    """Run backfill for specified tickers directly to DuckDB."""
    logger.info(f"🚀 Starting Supplemental Backfill for {len(tickers)} tickers to DuckDB...")
    
    try:
        # We use period="1mo" for supplemental refresh
        # to ensure we get a few days of buffer including today.
        # include_warrants=True locally, False on cloud (auto-handled)
        result = backfill_all_stocks(
            period="1mo",
            overwrite=True, 
            tickers=list(tickers)
        )
        
        if result.get("status") == "error":
            logger.error(f"❌ Backfill failed: {result.get('message')}")
        else:
            logger.info("✅ Supplemental backfill completed successfully.")
            
    except Exception as e:
        logger.error(f"❌ Failed to execute backfill: {e}")

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("📊 SMART SUPPLEMENTAL DATA REFRESH")
    logger.info("=" * 60)
    
    active_tickers = get_active_tickers()
    if not active_tickers:
        logger.error("❌ No tickers identified. Aborting.")
        sys.exit(1)
        
    run_supplemental_backfill(active_tickers)
    logger.info("🎉 Supplemental refresh cycle finished.")
