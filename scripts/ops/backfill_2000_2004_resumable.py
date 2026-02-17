
"""
Usage:
    nohup uv run python scripts/ops/backfill_2000_2004_resumable.py > /tmp/backfill_resumable.log 2>&1 &
"""
import sys
import os
import logging
import pandas as pd
from pathlib import Path

# Fix import path
sys.path.insert(0, os.getcwd())

from app.services.market_db import get_connection
from app.services.market_data_service import backfill_all_stocks, load_stock_list

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def backfill_resumable():
    logger.info("Checking DB state for resume...")
    conn = get_connection(read_only=True)
    
    # 1. Get current counts
    query = """
    SELECT stock_id, COUNT(*) as cnt 
    FROM daily_prices 
    WHERE date >= '2000-01-01' AND date < '2004-01-01'
    GROUP BY stock_id
    """
    try:
        df_counts = conn.execute(query).df()
        completed_tickers = set(df_counts[df_counts['cnt'] > 0]['stock_id'].tolist())
    except Exception as e:
        logger.warning(f"Failed to query DB: {e}. Assuming 0 completed.")
        completed_tickers = set()
    finally:
        conn.close()  # CRITICAL: Release DuckDB lock before backfill opens read-write
        
    logger.info(f"Found {len(completed_tickers)} stocks with existing data (completed).")
    
    # 2. Get full list
    stock_list = load_stock_list()
    all_codes = stock_list['code'].astype(str).tolist()
    
    todo = []
    for _, row in stock_list.iterrows():
        code = str(row['code']).strip()
        industry = str(row.get('industry', 'nan')).strip()
        
        # Filter completed
        if code in completed_tickers:
            continue
            
        # Filter warrants (Standard heuristic)
        # If code is 6 digits and industry is NaN -> Warrant
        if len(code) == 6 and industry == 'nan':
            continue
            
        todo.append(code)
            
    logger.info(f"Resume List: {len(todo)} tickers remaining.")
    
    if not todo:
        logger.info("All stocks have data or were attempted. Nothing to do.")
        return

    # 3. Running Backfill
    # chunks=1 for stability
    logger.info("Starting Resumable Backfill...")
    backfill_all_stocks(
        period="max",
        start_date="2000-01-01",
        end_date="2004-01-01",
        overwrite=True, 
        include_warrants=False,
        chunk_size=1,
        tickers=todo,
        progress_callback=lambda msg, pct: logger.info(f"[RESUME] {msg}")
    )

if __name__ == "__main__":
    backfill_resumable()
