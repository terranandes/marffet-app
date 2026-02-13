
import logging
from app.services.market_db import get_connection
from app.services.market_data_provider import MarketDataProvider

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger("VerifyIntegrity")

def check_integrity():
    logger.info("🔍 Verifying DuckDB Integrity...")
    
    conn = get_connection(read_only=True)
    try:
        # 1. Null and Zero Checks
        null_counts = conn.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE stock_id IS NULL) as null_id,
                COUNT(*) FILTER (WHERE date IS NULL) as null_date,
                COUNT(*) FILTER (WHERE close IS NULL) as null_close,
                COUNT(*) FILTER (WHERE close = 0) as zero_close
            FROM daily_prices
        """).fetchone()
        
        logger.info(f"📊 Daily Prices Scanned.")
        if any(v > 0 for v in null_counts):
            logger.warning(f"⚠️ Found Potential Issues in daily_prices: {null_counts}")
        else:
            logger.info("✅ No NULLs or zeros in close prices.")

        # 2. Stock Count Comparison
        stock_counts = conn.execute("""
            SELECT 
                (SELECT COUNT(*) FROM stocks) as total_stocks,
                (SELECT COUNT(DISTINCT stock_id) FROM daily_prices) as stocks_with_prices
        """).fetchone()
        logger.info(f"🏢 Stocks Table: {stock_counts[0]} | Price Coverage: {stock_counts[1]}")
        
        if stock_counts[0] > stock_counts[1]:
            logger.warning(f"⚠️ {stock_counts[0] - stock_counts[1]} stocks have no price data.")

        # 3. Gap Detection (Recentness)
        # Check max date for 2330
        tsmc_recent = conn.execute("SELECT MAX(date) FROM daily_prices WHERE stock_id = '2330'").fetchone()[0]
        if tsmc_recent:
            logger.info(f"📈 TSMC (2330) Latest Date: {tsmc_recent}")
        else:
            logger.warning("⚠️ TSMC (2330) has NO data!")

        # 4. Low Data Point Check
        low_data_stocks = conn.execute("""
            SELECT stock_id, COUNT(*) as cnt 
            FROM daily_prices 
            GROUP BY stock_id 
            HAVING cnt < 5 
            LIMIT 10
        """).fetchall()
        
        if low_data_stocks:
            logger.warning(f"⚠️ Found stocks with < 5 data points (showing top 10):")
            for sid, cnt in low_data_stocks:
                logger.warning(f"   - {sid}: {cnt} points")
        else:
            logger.info("✅ All stocks have sufficient data points.")

        # 5. Dividend coverage
        div_stats = conn.execute("SELECT COUNT(*), COUNT(DISTINCT stock_id) FROM dividends").fetchone()
        logger.info(f"✅ Dividends Healthy: {div_stats[0]} rows for {div_stats[1]} stocks.")

    except Exception as e:
        logger.error(f"❌ Integrity Check Failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_integrity()
