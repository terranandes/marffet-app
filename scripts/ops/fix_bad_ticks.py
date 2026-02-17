"""
Fix Bad Ticks (V-shape glitches) identified by `verify_splits_all.py`.

Logic:
1. Load `tests/analysis/bad_ticks.csv`.
2. For each row (stock_id, date), DELETE FROM daily_prices WHERE stock_id=? AND date=?.
3. Be careful with dates.

Usage:
    uv run python scripts/ops/fix_bad_ticks.py
"""

import duckdb
import pandas as pd
import os

CSV_PATH = 'tests/analysis/bad_ticks.csv'

if not os.path.exists(CSV_PATH):
    print(f"Error: {CSV_PATH} not found. Run verify_splits_all.py first.")
    exit(1)

df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df)} bad ticks to delete.")

if df.empty:
    print("No bad ticks to fix.")
    exit(0)

conn = duckdb.connect('data/market.duckdb')

print("Beginning DELETION of bad ticks...")

# We can construct a DELETE FROM ... WHERE (stock_id, date) IN (...) query
# DuckDB supports row-value constructors? Yes.
# Or just loop for safety / simplicity if count is small (<2000 is small).
# Actually, DELETE with WHERE IN ((...)) is faster.

delete_pairs = []
for _, row in df.iterrows():
    date_str = row['date']
    stock_id = row['stock_id']
    delete_pairs.append(f"('{stock_id}', '{date_str}')")

# Chunk it to avoid query length limits
CHUNK_SIZE = 500
deleted_count = 0

print(f"Executing in batches of {CHUNK_SIZE}...")
for i in range(0, len(delete_pairs), CHUNK_SIZE):
    chunk = delete_pairs[i:i+CHUNK_SIZE]
    in_clause = ",".join(chunk)
    q = f"DELETE FROM daily_prices WHERE (stock_id, date) IN ({in_clause})"
    
    # Execute
    conn.execute(q)
    print(f"Processed chunk {i}-{i+len(chunk)}")
    deleted_count += len(chunk)

print(f"Deletion complete. Processed {deleted_count} rows.")

# Verify 0050 bad tick (2024-01-25)
# Note: if verify_splits_all logic included 0050/2024-01-25, it should be gone.
print("\nVerifying 0050 2024-01-25 deletion...")
check = conn.execute("SELECT count(*) FROM daily_prices WHERE stock_id='0050' AND date='2024-01-25'").fetchone()[0]
print(f"0050 2024-01-25 count: {check} (Expected: 0 if it was in the file)")

conn.close()
