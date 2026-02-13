import logging
import os
import time
import sys
import json
import pandas as pd
from pathlib import Path

# Add the project root to sys.path to import app
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from app.services.market_db import get_connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def migrate_json_to_duckdb():
    start_time = time.time()
    logger.info("Starting JSON to DuckDB migration (V9 Arrow/Pandas Turbo)...")
    
    DB_PATH = project_root / "data/market.duckdb"
    if DB_PATH.exists(): os.remove(DB_PATH)
    
    conn = get_connection()
    conn.execute("""
        CREATE TABLE daily_prices (
            stock_id VARCHAR, date DATE, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume BIGINT, market VARCHAR
        );
        CREATE TABLE dividends (
            stock_id VARCHAR, year INTEGER, cash DOUBLE, stock DOUBLE
        );
        CREATE TABLE stocks (
            stock_id VARCHAR PRIMARY KEY, name VARCHAR, market_type VARCHAR, industry VARCHAR
        );
    """)
    conn.execute("SET memory_limit='3GB'")
    conn.execute("SET threads=8")

    data_dir = project_root / "data/raw"
    
    # 1. Stocks CSV
    stock_list_path = project_root / "app/project_tw/stock_list.csv"
    if stock_list_path.exists():
        logger.info("Loading stocks CSV...")
        conn.execute(f"INSERT INTO stocks SELECT code, name, market_type, industry FROM read_csv_auto('{stock_list_path}', all_varchar=True) ON CONFLICT DO NOTHING")
    
    stock_meta = [] # list of dicts for batch stock update

    # 2. Dividends
    div_files = sorted(list(data_dir.glob("*_Dividends_*.json")))
    logger.info(f"Loading {len(div_files)} dividend files via Pandas...")
    for d_file in div_files:
        try:
            year = int(d_file.stem.split("_")[-1])
            with open(d_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not data: continue
                df_div = pd.DataFrame.from_dict(data, orient='index')
                df_div['stock_id'] = df_div.index
                df_div['year'] = year
                df_div['cash'] = pd.to_numeric(df_div['cash'], errors='coerce').fillna(0)
                df_div['stock'] = pd.to_numeric(df_div['stock'], errors='coerce').fillna(0)
                conn.execute("INSERT INTO dividends SELECT stock_id, year, cash, stock FROM df_div")
        except: pass

    # 3. Prices
    price_files = sorted(list(data_dir.glob("*_Prices.json")))
    logger.info(f"Loading {len(price_files)} price files via Arrow/Pandas...")
    
    processed_stocks_set = set() # To track which stocks we already have names for

    total_all_prices = 0
    for i, p_file in enumerate(price_files):
        t0 = time.time()
        market = "TWSE" if "TPEx" not in p_file.name else "TPEx"
        parts = p_file.stem.split("_")
        year = 0
        for part in parts:
            if part.isdigit() and len(part) == 4:
                year = int(part)
                break
        
        if year == 0: continue
        
        with open(p_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            flat_prices = []
            
            # Robust check for data format
            if isinstance(data, list):
                # Format: [{"sid": "2330", "daily": [...]}, ...]
                nodes = {node.get('stock_id') or node.get('id'): node for node in data if node}
            else:
                nodes = data

            for sid, node in nodes.items():
                if not sid or not node: continue
                if sid not in processed_stocks_set:
                    name = node.get("name") or (node.get("summary") or {}).get("name") or ""
                    stock_meta.append({'stock_id': sid, 'name': name, 'market_type': market, 'industry': ''})
                    processed_stocks_set.add(sid)
                
                daily = node.get("daily")
                if isinstance(daily, list) and len(daily) > 0:
                    for d in daily:
                        flat_prices.append({'stock_id': sid, 'date': d['d'], 'open': d.get('o'), 'high': d.get('h'), 'low': d.get('l'), 'close': d.get('c'), 'volume': d.get('v'), 'market': market})
                else:
                    s = node.get("summary") or node
                    if isinstance(s, dict) and s.get('end'):
                        flat_prices.append({'stock_id': sid, 'date': f"{year}-12-31", 'open': s.get('start'), 'high': s.get('high'), 'low': s.get('low'), 'close': s.get('end'), 'volume': s.get('volume',0), 'market': market})
            
            if flat_prices:
                df_p = pd.DataFrame(flat_prices)
                df_p['date'] = pd.to_datetime(df_p['date'])
                conn.execute("INSERT INTO daily_prices SELECT * FROM df_p")
                total_all_prices += len(flat_prices)
                
        logger.info(f"  [{i+1}/{len(price_files)}] {p_file.name} - {len(flat_prices):,} rows in {time.time()-t0:.2f}s")
        if i % 10 == 0: conn.execute("CHECKPOINT")

    # 4. Final Updates
    if stock_meta:
        logger.info("Finalizing stock metadata...")
        df_meta = pd.DataFrame(stock_meta)
        conn.execute("INSERT INTO stocks SELECT * FROM df_meta ON CONFLICT DO NOTHING")

    # 5. Indexing (Deduplication pass)
    logger.info("Deduplicating and adding Primary Keys...")
    conn.execute("""
        CREATE TABLE dp_final AS SELECT * FROM daily_prices QUALIFY ROW_NUMBER() OVER (PARTITION BY stock_id, date ORDER BY close DESC) = 1;
        DROP TABLE daily_prices;
        ALTER TABLE dp_final RENAME TO daily_prices;
        ALTER TABLE daily_prices ADD PRIMARY KEY (stock_id, date);
    """)

    conn.close()
    logger.info(f"Migration Complete in {time.time() - start_time:.2f}s")
    logger.info(f"Total rows gathered: {total_all_prices:,}")

if __name__ == "__main__":
    migrate_json_to_duckdb()
