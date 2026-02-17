
import sys
import os
import pandas as pd
import logging

sys.path.insert(0, os.getcwd())
from app.services.market_db import get_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def verify_splits():
    conn = get_connection(read_only=True)
    
    # Check data volume
    count = conn.execute("SELECT COUNT(*) FROM daily_prices WHERE date >= '2000-01-01' AND date < '2004-01-01'").fetchone()[0]
    logger.info(f"Total rows in 2000-2004 range: {count}")
    
    if count < 1000:
        logger.error("Data volume too low. Backfill might be incomplete.")
        return

    logger.info("Scanning for Price Drops > 15%...")
    
    # DuckDB Window Function to find drops
    query = """
    WITH lagged AS (
        SELECT 
            stock_id, 
            date, 
            close, 
            LAG(close) OVER (PARTITION BY stock_id ORDER BY date) as prev_close
        FROM daily_prices
        WHERE date >= '2000-01-01' AND date < '2004-01-01'
    )
    SELECT 
        stock_id, 
        date, 
        close, 
        prev_close, 
        (close - prev_close)/prev_close as pct_chg 
    FROM lagged 
    WHERE pct_chg < -0.08 
    ORDER BY stock_id, date
    """
    
    drops = conn.execute(query).df()
    logger.info(f"Found {len(drops)} potential split events (drops > 8%).")
    
    missing_records = []
    mismatched_records = []
    
    for _, row in drops.iterrows():
        sid = row['stock_id']
        date = row['date']
        year = date.year
        drop = row['pct_chg']
        prev_c = row['prev_close']
        curr_c = row['close']
        
        # Check dividends for this year (or previous year if early Jan?)
        # Dividend Year usually matches payment year. ex-date is determining factor.
        recs = conn.execute(f"SELECT * FROM dividends WHERE stock_id='{sid}' AND year={year}").fetchall()
        
        if not recs:
            # Check previous year if date is Jan?
            if date.month == 1:
                recs_prev = conn.execute(f"SELECT * FROM dividends WHERE stock_id='{sid}' AND year={year-1}").fetchall()
                if recs_prev: recs = recs_prev
        
        implied_ratio = prev_c / curr_c
        
        if not recs:
            logger.warning(f"MISSING RECORD: {sid} on {date} dropped {drop*100:.1f}%. Implied Split: {implied_ratio:.2f}")
            missing_records.append({
                'stock_id': sid, 'date': date, 'drop_pct': drop, 'implied_ratio': implied_ratio
            })
        else:
            # Record Exists. Check consistency.
            # Schema: stock_id, year, cash, stock
            # Stock div 1.0 means 100%? (Split 2.0). 
            # Or stock div 0.1 means 10%? (Split 1.1).
            # Assuming 'stock' column is "Shares per 1 share" (e.g. 0.1) or "Shares per 10"?
            # We assume it follows market_data_service logic: stock += (split_val - 1.0)
            # So stored value corresponds to (Ratio - 1).
            # E.g. Split 1.25 -> Stored 0.25.
            
            # Let's verify sum of stock divs for that year
            total_stock_div = sum(r[3] for r in recs) # index 3 is stock
            recorded_ratio = 1.0 + total_stock_div
            
            # Allow 10% margin (price fluctuations + cash div impact)
            # Implied Ratio vs Recorded Ratio
            diff = abs(implied_ratio - recorded_ratio) / recorded_ratio
            
            if diff > 0.15:
                 logger.warning(f"MISMATCH: {sid} on {date}. Drop {drop*100:.1f}% -> Implied {implied_ratio:.2f}. Record {recorded_ratio:.2f}. Diff {diff*100:.1f}%")
                 mismatched_records.append({
                     'stock_id': sid, 'date': date, 'drop_pct': drop, 
                     'implied_ratio': implied_ratio, 'recorded_ratio': recorded_ratio
                 })

    # Save Reports
    if missing_records:
        pd.DataFrame(missing_records).to_csv("tests/analysis/missing_splits_2000_2004.csv", index=False)
        logger.info("Saved tests/analysis/missing_splits_2000_2004.csv")
        
    if mismatched_records:
        pd.DataFrame(mismatched_records).to_csv("tests/analysis/mismatched_splits_2000_2004.csv", index=False)
        logger.info("Saved tests/analysis/mismatched_splits_2000_2004.csv")

if __name__ == "__main__":
    verify_splits()
