with open("app/services/market_db.py", "r") as f:
    text = f.read()

def_resolve = """def _rehydrate_from_parquet(target_db: Path):
    \"\"\"Rebuild the DuckDB database from Parquet backups if empty.\"\"\"
    backup_dir = BASE_DIR / "data" / "backup"
    if not backup_dir.exists():
        logging.warning("[MarketDB] No Parquet backups found for rehydration.")
        return

    logging.info(f"[MarketDB] Rehydrating {target_db} from Parquet backups...")
    target_db.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(target_db))
    try:
        # 1. daily_prices
        conn.execute(\"\"\"
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
        \"\"\")
        
        # 2. dividends
        conn.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS dividends (
                stock_id VARCHAR,
                year INTEGER,
                cash DOUBLE,
                stock DOUBLE,
                PRIMARY KEY (stock_id, year)
            )
        \"\"\")
        
        # 3. stocks
        conn.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS stocks (
                stock_id VARCHAR PRIMARY KEY,
                name VARCHAR,
                market_type VARCHAR,
                industry VARCHAR
            )
        \"\"\")

        # Load daily_prices
        price_files = list(backup_dir.glob("prices_*.parquet"))
        if price_files:
            logging.info(f"[MarketDB] Restoring {len(price_files)} daily_prices parquets...")
            conn.execute(f"INSERT INTO daily_prices SELECT * FROM read_parquet('{backup_dir}/prices_*.parquet')")
            
        # Load dividends
        div_file = backup_dir / "dividends.parquet"
        if div_file.exists():
            logging.info("[MarketDB] Restoring dividends parquet...")
            conn.execute(f"INSERT INTO dividends SELECT * FROM read_parquet('{div_file}')")
            
        # Load stocks
        stock_file = backup_dir / "stocks.parquet"
        if stock_file.exists():
            logging.info("[MarketDB] Restoring stocks parquet...")
            conn.execute(f"INSERT INTO stocks SELECT * FROM read_parquet('{stock_file}')")
            
        logging.info("[MarketDB] Rehydration complete.")
    except Exception as e:
        logging.error(f"[MarketDB] Rehydration failed: {e}")
        raise
    finally:
        conn.close()

def _resolve_db_path() -> Path:
    \"\"\"Resolve the best DuckDB path, with copy-on-startup for Zeabur.\"\"\"
    # If /data/ volume exists (Zeabur), use it
    if _VOLUME_DB_PATH.parent.exists() and _VOLUME_DB_PATH.parent.is_dir():
        if not _VOLUME_DB_PATH.exists():
            if _LOCAL_DB_PATH.exists():
                logging.info(f"[MarketDB] Copying {_LOCAL_DB_PATH} → {_VOLUME_DB_PATH}")
                shutil.copy2(str(_LOCAL_DB_PATH), str(_VOLUME_DB_PATH))
            else:
                _rehydrate_from_parquet(_VOLUME_DB_PATH)
        return _VOLUME_DB_PATH
    
    # Fallback: local development path
    if not _LOCAL_DB_PATH.exists():
        _rehydrate_from_parquet(_LOCAL_DB_PATH)
    return _LOCAL_DB_PATH
"""

old_resolve = """def _resolve_db_path() -> Path:
    \"\"\"Resolve the best DuckDB path, with copy-on-startup for Zeabur.\"\"\"
    # If /data/ volume exists (Zeabur), use it
    if _VOLUME_DB_PATH.parent.exists() and _VOLUME_DB_PATH.parent.is_dir():
        if not _VOLUME_DB_PATH.exists() and _LOCAL_DB_PATH.exists():
            # First deploy: copy bundled DB to persistent volume
            logging.info(f"[MarketDB] Copying {_LOCAL_DB_PATH} → {_VOLUME_DB_PATH} (first deploy)")
            shutil.copy2(str(_LOCAL_DB_PATH), str(_VOLUME_DB_PATH))
        if _VOLUME_DB_PATH.exists():
            return _VOLUME_DB_PATH
    # Fallback: local development path
    return _LOCAL_DB_PATH"""

text = text.replace(old_resolve, def_resolve)

with open("app/services/market_db.py", "w") as f:
    f.write(text)

