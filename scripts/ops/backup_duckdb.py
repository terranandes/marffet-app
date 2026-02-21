import duckdb
import os
from pathlib import Path
import logging

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data/market.duckdb"
BACKUP_DIR = BASE_DIR / "data/backup"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def backup():
    if not DB_PATH.exists():
        logging.error(f"Database not found at {DB_PATH}")
        return

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    
    try:
        # Get all distinct years in daily_prices
        logging.info("Gathering distinct years from daily_prices...")
        years_query = "SELECT DISTINCT EXTRACT(YEAR FROM date)::INTEGER as year FROM daily_prices ORDER BY year"
        years = [row[0] for row in conn.execute(years_query).fetchall()]
        
        logging.info(f"Backing up daily_prices for years: {years}")
        
        for year in years:
            parquet_path = BACKUP_DIR / f"prices_{year}.parquet"
            conn.execute(f"COPY (SELECT * FROM daily_prices WHERE EXTRACT(YEAR FROM date)::INTEGER = {year}) TO '{parquet_path}' (FORMAT PARQUET)")
            logging.info(f"Exported {parquet_path.name}")
            
        # Also backup dividends and stocks tables
        dividends_path = BACKUP_DIR / "dividends.parquet"
        conn.execute(f"COPY (SELECT * FROM dividends) TO '{dividends_path}' (FORMAT PARQUET)")
        logging.info(f"Exported {dividends_path.name}")
        
        stocks_path = BACKUP_DIR / "stocks.parquet"
        conn.execute(f"COPY (SELECT * FROM stocks) TO '{stocks_path}' (FORMAT PARQUET)")
        logging.info(f"Exported {stocks_path.name}")
        
        logging.info("Backup complete. Add these Parquet files to git.")
        
    finally:
        conn.close()

if __name__ == "__main__":
    backup()
