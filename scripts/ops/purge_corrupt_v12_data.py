"""
Purge corrupt V12 backfill data (pre-2005) for stocks that failed the 2005-01-03 continuity check.

Logic:
1. Load `tests/analysis/cliff_stocks_2005.csv`.
2. Filter for stocks with ABS(pct_change) > 0.5 (50% drop or gain).
3. For each stock, DELETE FROM daily_prices WHERE stock_id=? AND date < '2005-01-01'.
4. DELETE FROM dividends WHERE stock_id=? AND year < 2005.
"""

import duckdb
import pandas as pd
import os

CSV_PATH = 'tests/analysis/cliff_stocks_2005.csv'

# Check if file exists
if not os.path.exists(CSV_PATH):
    print(f"Error: {CSV_PATH} not found.")
    exit(1)

# Load CSV
df = pd.read_csv(CSV_PATH)
targets = df[df['pct_change'].abs() > 0.5]['stock_id'].unique().tolist()
print(f"Loaded {len(targets)} stocks to purge (ABS > 50% cliff).")

if not targets:
    print("No stocks to purge.")
    exit(0)

conn = duckdb.connect('data/market.duckdb')

print("Beginning PURGE of pre-2005 data for listed stocks...")

# Construct SQL IN list manually (DuckDB params can be finicky for lists)
target_list = ",".join([f"'{s}'" for s in targets])

q_prices = f"DELETE FROM daily_prices WHERE date < '2005-01-01' AND stock_id IN ({target_list})"
print(f"Executing DELETE prices for {len(targets)} stocks...")
conn.execute(q_prices)

q_divs = f"DELETE FROM dividends WHERE year < 2005 AND stock_id IN ({target_list})"
print(f"Executing DELETE dividends for {len(targets)} stocks...")
conn.execute(q_divs)

# Verify
rem_pre_2005 = conn.execute("SELECT count(*) FROM daily_prices WHERE date < '2005-01-01'").fetchone()[0]
print(f"Purge complete. Remaining pre-2005 prices (all stocks): {rem_pre_2005}")

# Check 3701 specifically
check_3701 = conn.execute("SELECT count(*) FROM daily_prices WHERE stock_id='3701' AND date < '2005-01-01'").fetchone()[0]
print(f"3701 pre-2005 count: {check_3701} (Expected: 0)")

conn.close()
