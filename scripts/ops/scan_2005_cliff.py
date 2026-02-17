"""
Identify stocks with a '2005 Cliff' (Massive drop/gain on 2005-01-03).
These likely have corrupt V12 backfill data (2000-2004).
Action: Generate list for PURGE.
"""

import duckdb
import pandas as pd

conn = duckdb.connect('data/market.duckdb', read_only=True)

print("Scanning for 2005-01-03 Data Cliff...")

# Get close price on last day of 2004 and first day of 2005
q = """
WITH last_2004 AS (
    SELECT stock_id, close as close_2004, date
    FROM daily_prices 
    WHERE date BETWEEN '2004-12-20' AND '2004-12-31'
    QUALIFY ROW_NUMBER() OVER (PARTITION BY stock_id ORDER BY date DESC) = 1
),
first_2005 AS (
    SELECT stock_id, close as close_2005, date
    FROM daily_prices 
    WHERE date BETWEEN '2005-01-01' AND '2005-01-10'
    QUALIFY ROW_NUMBER() OVER (PARTITION BY stock_id ORDER BY date ASC) = 1
)
SELECT 
    a.stock_id, 
    a.close_2004, 
    b.close_2005,
    (b.close_2005 - a.close_2004) / a.close_2004 as pct_change
FROM last_2004 a
JOIN first_2005 b ON a.stock_id = b.stock_id
WHERE ABS((b.close_2005 - a.close_2004) / a.close_2004) > 0.5
ORDER BY pct_change ASC
"""

cliff_stocks = conn.execute(q).df()

print(f"\nFound {len(cliff_stocks)} stocks with >50% discontinuity at 2005 boundary:")
print(cliff_stocks.to_string(index=False))

# Also save to CSV
cliff_stocks.to_csv('tests/analysis/cliff_stocks_2005.csv', index=False)
