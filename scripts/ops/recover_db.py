import duckdb
import glob
import os

DB_PATH = 'data/market.duckdb'
BACKUP_DIR = 'data/backup'

def recover_prices():
    if not os.path.exists(BACKUP_DIR):
        print("❌ Backup directory not found!")
        return

    parquet_files = glob.glob(f"{BACKUP_DIR}/prices_*.parquet")
    if not parquet_files:
        print("❌ No parquet backup files found!")
        return

    print(f"📖 Found {len(parquet_files)} backup files. Preparing restoration...")
    
    conn = duckdb.connect(DB_PATH)
    
    # Check current count
    try:
        old_count = conn.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
        print(f"📊 Current corrupted records: {old_count}")
    except:
        old_count = 0

    print("🗑️  Emptying daily_prices table...")
    conn.execute("DELETE FROM daily_prices")
    
    # Load all parquet files into a TEMP table to avoid inserting duplicates if any exist
    print("⏳ Loading Parquet data into Temp Table...")
    conn.execute(f"CREATE TEMP TABLE temp_prices AS SELECT * FROM read_parquet('{BACKUP_DIR}/prices_*.parquet')")
    
    temp_count = conn.execute("SELECT COUNT(*) FROM temp_prices").fetchone()[0]
    print(f"📊 Parquet Backup has {temp_count} records.")

    print("💾 Restoring to daily_prices...")
    # Use INSERT OR REPLACE if there's a unique constraint, otherwise just INSERT. 
    # daily_prices has (stock_id, date) Primary Key in schema (or should).
    conn.execute("""
        INSERT INTO daily_prices (stock_id, date, open, high, low, close, change, volume)
        SELECT stock_id, date, open, high, low, close, change, volume FROM temp_prices
    """)

    new_count = conn.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
    
    print(f"✅ Restoration Complete!")
    print(f"   Before (Corrupted): {old_count}")
    print(f"   After  (Restored) : {new_count}")

    # Spot check 8066
    print("\n🔍 Spot Check - 8066 (Should NOT be 8.02):")
    print(conn.execute("SELECT * FROM daily_prices WHERE stock_id='8066' ORDER BY date LIMIT 5").df())

    conn.close()

if __name__ == "__main__":
    recover_prices()
