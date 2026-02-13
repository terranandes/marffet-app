import duckdb
import logging
import os
from pathlib import Path

# Path to the DuckDB database file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data/market.duckdb"

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
