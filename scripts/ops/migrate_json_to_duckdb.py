import json
import logging
import os
import time
import sys
import csv
from pathlib import Path
from typing import Dict, Any, List, Set

# Add the project root to sys.path to import app
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from app.services.market_db import get_connection, init_schema

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def migrate_json_to_duckdb():
    start_time = time.time()
    logger.info("Starting JSON to DuckDB migration...")
    
    # Initialize schema and get connection
    init_schema()
    conn = get_connection()
    
    # Configure DuckDB for performance
    conn.execute("SET memory_limit='400MB'")
    conn.execute("SET threads=1")
    conn.execute("SET preserve_insertion_order=false")
    conn.execute("SET temp_directory='data/tmp'")
    os.makedirs('data/tmp', exist_ok=True)
    
    data_dir = project_root / "data/raw"
    stock_list_path = project_root / "app/project_tw/stock_list.csv"
    
    total_prices_rows = 0
    total_dividends_rows = 0
    distinct_stocks = set()
    
    # 1. Populate stocks table from stock_list.csv
    if stock_list_path.exists():
        logger.info(f"Loading stock list from {stock_list_path}...")
        try:
            with open(stock_list_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                stock_rows = []
                for row in reader:
                    code = row.get('code', '').strip()
                    if not code: continue
                    name = row.get('name', '').strip()
                    mtype = row.get('market_type', '').strip()
                    industry = row.get('industry', '').strip()
                    if industry.lower() == 'nan': industry = ""
                    
                    # Only add to stock_rows if not already processed to avoid redundant updates
                    if code not in distinct_stocks:
                        stock_rows.append((code, name, mtype, industry))
                        distinct_stocks.add(code)
                    
                    if len(stock_rows) >= 1000:
                        conn.executemany("""
                            INSERT INTO stocks (stock_id, name, market_type, industry)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT (stock_id) DO UPDATE SET
                                name = EXCLUDED.name,
                                market_type = EXCLUDED.market_type,
                                industry = EXCLUDED.industry
                        """, stock_rows)
                        stock_rows = []
                
                if stock_rows:
                    conn.executemany("""
                        INSERT INTO stocks (stock_id, name, market_type, industry)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT (stock_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            market_type = EXCLUDED.market_type,
                            industry = EXCLUDED.industry
                    """, stock_rows)
            logger.info(f"Loaded {len(distinct_stocks)} stocks from CSV.")
        except Exception as e:
            logger.error(f"Error loading stock list CSV: {e}")

    # 2. Process Dividend Files
    dividend_files = sorted(list(data_dir.glob("*_Dividends_*.json")))
    logger.info(f"Found {len(dividend_files)} dividend files.")
    
    for d_file in dividend_files:
        new_stocks_batch = []
        try:
            parts = d_file.stem.split("_")
            year_str = parts[-1]
            if not year_str.isdigit(): continue
            year = int(year_str)
            
            with open(d_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not data: continue
            
            div_rows = []
            for stock_id, node in data.items():
                # Add stock_id to distinct_stocks if not already present
                if stock_id not in distinct_stocks:
                    # For dividends, we don't have full stock info, so we insert with minimal data
                    new_stocks_batch.append((stock_id, "", "", ""))
                    distinct_stocks.add(stock_id)

                div_rows.append((
                    stock_id,
                    year,
                    float(node.get("cash", 0.0) or 0.0),
                    float(node.get("stock", 0.0) or 0.0)
                ))
            
            if new_stocks_batch:
                conn.executemany("""
                    INSERT INTO stocks (stock_id, name, market_type, industry)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT (stock_id) DO NOTHING
                """, new_stocks_batch)

            if div_rows:
                conn.execute("BEGIN TRANSACTION")
                conn.executemany("""
                    INSERT INTO dividends (stock_id, year, cash, stock)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT (stock_id, year) DO UPDATE SET
                        cash = EXCLUDED.cash,
                        stock = EXCLUDED.stock
                """, div_rows)
                conn.execute("COMMIT")
                total_dividends_rows += len(div_rows)
            
            logger.info(f"Processed dividends for {d_file.name}")
            del data
            del div_rows
            import gc
            gc.collect()
        except Exception as e:
            logger.error(f"Error processing {d_file.name}: {e}")
            try: conn.execute("ROLLBACK")
            except: pass
    
    # 3. Process Price Files
    price_files = sorted(list(data_dir.glob("*_Prices.json")))
    logger.info(f"Found {len(price_files)} price files.")
    
    for i, p_file in enumerate(price_files):
        try:
            market = "TWSE"
            if "TPEx" in p_file.name:
                market = "TPEx"
            
            parts = p_file.stem.split("_")
            year = 0
            for part in parts:
                if part.isdigit() and len(part) == 4:
                    year = int(part)
                    break
            
            if year == 0: continue
                
            logger.info(f"[{i+1}/{len(price_files)}] Processing {p_file.name}...")
            
            with open(p_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not data: continue
            
            daily_rows = []
            
            stock_updates = []
            for stock_id, node in data.items():
                if stock_id not in distinct_stocks:
                    market_type = "Listed" if "Market" in p_file.name and "TPEx" not in p_file.name else "OTC"
                    stock_updates.append((stock_id, "", market_type, ""))
                    distinct_stocks.add(stock_id)
            
            if stock_updates:
                conn.executemany("""
                    INSERT INTO stocks (stock_id, name, market_type, industry)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT (stock_id) DO NOTHING
                """, stock_updates)
                
                # Extract daily data (V2)
                if isinstance(node, dict) and "daily" in node and node["daily"]:
                    for day in node["daily"]:
                        daily_rows.append((
                            stock_id,
                            day["d"],
                            float(day.get("o") or 0.0) if day.get("o") is not None else None,
                            float(day.get("h") or 0.0) if day.get("h") is not None else None,
                            float(day.get("l") or 0.0) if day.get("l") is not None else None,
                            float(day.get("c") or 0.0) if day.get("c") is not None else None,
                            int(day.get("v") or 0) if day.get("v") is not None else 0,
                            market
                        ))
                # Fallback to Summary (V1)
                elif isinstance(node, dict):
                    s = node.get("summary") if isinstance(node.get("summary"), dict) else node
                    open_p, close_p = s.get("start") or s.get("first_open"), s.get("end")
                    high_p, low_p = s.get("high"), s.get("low")
                    vol = s.get("volume", 0)
                    
                    if open_p is not None or close_p is not None:
                        daily_rows.append((stock_id, f"{year}-12-31", float(open_p or 0), float(high_p or 0), 
                                         float(low_p or 0), float(close_p or 0), int(vol or 0), market))

            # Batch insert daily prices
            if daily_rows:
                logger.info(f"  Inserting {len(daily_rows)} price rows...")
                for j in range(0, len(daily_rows), 100000):
                    batch = daily_rows[j:j+100000]
                    conn.execute("BEGIN TRANSACTION")
                    conn.executemany("""
                        INSERT INTO daily_prices (stock_id, date, open, high, low, close, volume, market)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT (stock_id, date) DO UPDATE SET
                            open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low,
                            close = EXCLUDED.close, volume = EXCLUDED.volume, market = EXCLUDED.market
                    """, batch)
                    conn.execute("COMMIT")
                total_prices_rows += len(daily_rows)
                logger.info(f"   Inserted {len(daily_rows)} rows for {year} {market}.")
            
            # Explicitly clear data to free memory
            del data
            del daily_rows
            import gc
            gc.collect()
                
        except Exception as e:
            logger.error(f"Error processing {p_file.name}: {e}")
            try: conn.execute("ROLLBACK")
            except: pass

    # 4. Process Race Cache (SQLite) for Historical Monthly Data
    try:
        sqlite_path = project_root / "data/portfolio.db"
        if sqlite_path.exists():
            import sqlite3
            logger.info("Migrating Race Cache (Monthly Closes) from portfolio.db...")
            with sqlite3.connect(sqlite_path) as s_conn:
                cursor = s_conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='race_cache'")
                if cursor.fetchone():
                    rows = cursor.execute("SELECT stock_id, month, close_price FROM race_cache WHERE month < '2024-01'").fetchall()
                    race_batch = []
                    for r in rows:
                        sid, month, price = r
                        if month == 'ERROR' or not price: continue
                        try:
                            p_val = float(price)
                            # Store as 1st of month to avoid date conflicts with YYYY-12-31 summary
                            # This provides ~12 points/year for volatility instead of 1
                            race_batch.append((
                                sid, f"{month}-01", 
                                p_val, p_val, p_val, p_val, 0, 'Unknown'
                            ))
                        except: pass
                    
                    if race_batch:
                        logger.info(f"  Inserting {len(race_batch)} monthly rows from race_cache...")
                        conn.execute("BEGIN TRANSACTION")
                        conn.executemany("""
                            INSERT INTO daily_prices (stock_id, date, open, high, low, close, volume, market)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT (stock_id, date) DO NOTHING
                        """, race_batch)
                        conn.execute("COMMIT")
                        total_prices_rows += len(race_batch)
                        logger.info(f"   Inserted {len(race_batch)} historical monthly rows.")
    except Exception as e:
        logger.error(f"Error migrating race cache: {e}")

    # 5. Final Validation
    db_prices_count = conn.execute("SELECT count(*) FROM daily_prices").fetchone()[0]
    db_div_count = conn.execute("SELECT count(*) FROM dividends").fetchone()[0]
    db_stocks_count = conn.execute("SELECT count(*) FROM stocks").fetchone()[0]
    
    conn.close()
    
    duration = time.time() - start_time
    logger.info("=" * 40)
    logger.info(f"Migration Complete in {duration:.2f}s")
    logger.info(f"Price Rows (All): {db_prices_count}")
    logger.info(f"Dividend Rows: {db_div_count}")
    logger.info(f"Distinct Stocks: {db_stocks_count}")
    logger.info("=" * 40)

if __name__ == "__main__":
    migrate_json_to_duckdb()
