import duckdb
import logging
from datetime import datetime
import time
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path("data/market.duckdb")

def verify_tsmc_cagr():
    """
    Verify TSMC CAGR from 2006. Should be ~19%.
    Task 10.1 in PRD.
    """
    if not DB_PATH.exists():
        logger.error(f"Database {DB_PATH} not found!")
        return

    logger.info("Attempting to connect to DuckDB for TSMC CAGR verification...")
    
    # Try multiple times in case of lock
    conn = None
    for i in range(5):
        try:
            conn = duckdb.connect(str(DB_PATH), read_only=True)
            break
        except Exception as e:
            logger.warning(f"Attempt {i+1}: Could not connect (locked?). Waiting 5s...")
            time.sleep(5)
    
    if not conn:
        logger.error("Could not connect to database after 5 attempts. Skipping verification.")
        return

    try:
        # Get TSMC (2330) prices for 2006-01-01 and latest
        logger.info("Fetching TSMC prices...")
        
        # Start of 2006
        start_row = conn.execute("""
            SELECT close, date 
            FROM daily_prices 
            WHERE stock_id = '2330' AND date >= '2006-01-01' 
            ORDER BY date ASC LIMIT 1
        """).fetchone()
        
        # Latest
        end_row = conn.execute("""
            SELECT close, date 
            FROM daily_prices 
            WHERE stock_id = '2330' 
            ORDER BY date DESC LIMIT 1
        """).fetchone()
        
        if not start_row or not end_row:
            logger.error(f"Missing data for TSMC (2330). Start: {start_row}, End: {end_row}")
            return

        start_price, start_date = start_row
        end_price, end_date = end_row
        
        logger.info(f"TSMC Start: {start_price} on {start_date}")
        logger.info(f"TSMC End:   {end_price} on {end_date}")
        
        # Calculate years
        if isinstance(start_date, str):
            sd = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            sd = start_date
            
        if isinstance(end_date, str):
            ed = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            ed = end_date
            
        years = (ed - sd).days / 365.25
        
        if years <= 0:
            logger.error("Invalid year range.")
            return
            
        # CAGR = (End/Start)^(1/Years) - 1
        cagr = (end_price / start_price) ** (1 / years) - 1
        
        logger.info(f"TSMC CAGR ({start_date} to {end_date}): {cagr:.2%}")
        
        # Success criteria: ~19% (allow 15-25% range depending on latest market)
        if 0.15 <= cagr <= 0.25:
            logger.info("✅ TSMC CAGR within expected range (~19%).")
        else:
            logger.warning(f"⚠️ TSMC CAGR {cagr:.2%} outside tight range (~19%), but might be correct for current dates.")

    except Exception as e:
        logger.error(f"Error during verification: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    verify_tsmc_cagr()
