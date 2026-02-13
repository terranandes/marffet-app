import duckdb
import logging
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path("data/market.duckdb")

def verify_volatility_data():
    """
    Verify Mars Strategy uses real daily data for volatility.
    Task 10.2 in PRD.
    """
    if not DB_PATH.exists():
        logger.error(f"Database {DB_PATH} not found!")
        return

    conn = None
    try:
        conn = duckdb.connect(str(DB_PATH), read_only=True)
    except Exception as e:
        logger.error(f"Could not connect: {e}")
        return

    try:
        # Check TSMC daily data count
        logger.info("Checking daily price row count for TSMC (2330)...")
        row_count = conn.execute("SELECT COUNT(*) FROM daily_prices WHERE stock_id = '2330'").fetchone()[0]
        
        logger.info(f"TSMC Row Count: {row_count}")
        
        # Success criteria: > 4000 rows for 20+ years of data
        if row_count > 4000:
            logger.info(f"✅ TSMC Has {row_count} daily rows. Volatility calculation will be accurate (Expected ~5000).")
        elif row_count > 0:
            logger.warning(f"⚠️ TSMC Has only {row_count} rows. Migration might still be in progress.")
        else:
            logger.error("❌ TSMC Has 0 rows in daily_prices.")

        # Verify that we have daily data (not just monthly placeholders)
        if row_count > 100:
            # Check a sample of consecutive days
            logger.info("Verifying date frequency...")
            dates = conn.execute("""
                SELECT date FROM daily_prices 
                WHERE stock_id = '2330' AND date >= '2023-01-01' AND date <= '2023-01-31'
                ORDER BY date
            """).fetchall()
            
            if len(dates) > 10:
                logger.info(f"✅ Found {len(dates)} trading days in Jan 2023. Confirmed DAILY data.")
            else:
                logger.error(f"❌ Found only {len(dates)} days in Jan 2023. Might be monthly/sparse data.")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    verify_volatility_data()
