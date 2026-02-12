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

def run_incremental_crawl(tickers):
    """Run crawl_fast.py in incremental mode for specified tickers."""
    ticker_list = ",".join(sorted(list(tickers)))
    logger.info(f"🚀 Starting Incremental Crawl for {len(tickers)} tickers...")
    
    # We use 'uv run' to ensure dependencies are loaded
    cmd = [
        "uv", "run", "python", str(CRAWLER_SCRIPT),
        "--mode", "incremental",
        "--days", "10",
        "--tickers", ticker_list
    ]
    
    try:
        # Run and capture output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(PROJECT_ROOT)
        )
        
        # Stream output to log
        for line in process.stdout:
            print(f"   [Crawler] {line.strip()}")
            
        process.wait()
        
        if process.returncode == 0:
            logger.info("✅ Incremental crawl completed successfully.")
        else:
            logger.error(f"❌ Crawler exited with code {process.returncode}")
            
    except Exception as e:
        logger.error(f"❌ Failed to execute crawler: {e}")

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("📊 SMART SUPPLEMENTAL DATA REFRESH")
    logger.info("=" * 60)
    
    active_tickers = get_active_tickers()
    if not active_tickers:
        logger.error("❌ No tickers identified. Aborting.")
        sys.exit(1)
        
    run_incremental_crawl(active_tickers)
    logger.info("🎉 Supplemental refresh cycle finished.")
