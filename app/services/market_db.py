import duckdb
import logging
import os
import shutil
from pathlib import Path

# Path to the DuckDB database file
# Priority: /data/market.duckdb (Zeabur persistent volume) > project-local data/market.duckdb
BASE_DIR = Path(__file__).resolve().parent.parent.parent
_VOLUME_DB_PATH = Path("/data/market.duckdb")
_LOCAL_DB_PATH = BASE_DIR / "data/market.duckdb"

def _resolve_db_path() -> Path:
    """Resolve the best DuckDB path, with copy-on-startup for Zeabur."""
    # If /data/ volume exists (Zeabur), use it
    if _VOLUME_DB_PATH.parent.exists() and _VOLUME_DB_PATH.parent.is_dir():
        if not _VOLUME_DB_PATH.exists() and _LOCAL_DB_PATH.exists():
            # First deploy: copy bundled DB to persistent volume
            logging.info(f"[MarketDB] Copying {_LOCAL_DB_PATH} → {_VOLUME_DB_PATH} (first deploy)")
            shutil.copy2(str(_LOCAL_DB_PATH), str(_VOLUME_DB_PATH))
        if _VOLUME_DB_PATH.exists():
            return _VOLUME_DB_PATH
    # Fallback: local development path
    return _LOCAL_DB_PATH

DB_PATH = _resolve_db_path()

def get_connection(read_only: bool = False):
    """
    Get a connection to the DuckDB database.
    """
    # Ensure directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH), read_only=read_only)

def init_schema():
    """
    Initialize the DuckDB schema with required tables.
    """
    logging.info(f"[MarketDB] Initializing schema at {DB_PATH}")
    
    conn = get_connection()
    try:
        # 1. daily_prices table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_prices (
                stock_id VARCHAR,
                date DATE,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                change DOUBLE,
                volume BIGINT,
                market VARCHAR,
                PRIMARY KEY (stock_id, date)
            )
        """)
        
        # 2. dividends table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dividends (
                stock_id VARCHAR,
                year INTEGER,
                cash DOUBLE,
                stock DOUBLE,
                PRIMARY KEY (stock_id, year)
            )
        """)
        
        # 3. stocks table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                stock_id VARCHAR PRIMARY KEY,
                name VARCHAR,
                market_type VARCHAR,
                industry VARCHAR
            )
        """)
        
        logging.info("[MarketDB] Schema initialized successfully.")
    except Exception as e:
        logging.error(f"[MarketDB] Error initializing schema: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Setup basic logging for standalone execution
    logging.basicConfig(level=logging.INFO)
    init_schema()
