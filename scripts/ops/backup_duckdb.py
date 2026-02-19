import duckdb
import os

BACKUP_DIR = 'data/backup'
os.makedirs(BACKUP_DIR, exist_ok=True)
conn = duckdb.connect('data/market.duckdb', read_only=True)

try:
    years = conn.execute("SELECT DISTINCT EXTRACT(year FROM date)::INT AS yr FROM daily_prices ORDER BY yr").fetchall()
except Exception as e:
    print(f"Error fetching years: {e}")
    years = []

print(f"Found {len(years)} years of data.")

for (y,) in years:
    target_file = f"{BACKUP_DIR}/prices_{y}.parquet"
    print(f"Exporting {y} -> {target_file} ...")
    conn.execute(f"COPY (SELECT * FROM daily_prices WHERE EXTRACT(year FROM date) = {y}) TO '{target_file}' (FORMAT 'parquet')")

print("Backup complete.")
