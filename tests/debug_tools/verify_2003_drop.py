
import sys
import os
sys.path.insert(0, os.getcwd())
from app.services.market_db import get_connection

conn = get_connection(read_only=True)
stock_id = '2330'
year = 2003

print(f"--- Checking {stock_id} for {year} ---")

# 1. Check Dividend Record
divs = conn.execute(f"SELECT * FROM dividends WHERE stock_id = '{stock_id}' AND year = {year}").fetchall()
print(f"Dividends {year}: {divs}")
# Expected: Cash ~0.6, Stock ~0.8?

# 2. Check Prices around Ex-Div
# We don't know exact date, so let's dump June-July
print(f"\nPrices 2003-06 to 2003-07:")
rows = conn.execute(f"SELECT date, close, high, low FROM daily_prices WHERE stock_id = '{stock_id}' AND date >= '2003-06-01' AND date <= '2003-07-31' ORDER BY date").fetchall()

for r in rows:
    print(r)

# 3. Analyze Drops
print("\nScanning for drops > 5%...")
for i in range(1, len(rows)):
    prev_c = rows[i-1][1]
    curr_c = rows[i][1]
    date = rows[i][0]
    
    drop = (curr_c - prev_c) / prev_c
    if drop < -0.05:
        print(f"Values on {date}: {prev_c} -> {curr_c} ({drop*100:.1f}%)")

conn.close()
