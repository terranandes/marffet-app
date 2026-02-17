"""
Verify and Detect Missing Splits / Bad Ticks (2000-2025)

Logic:
1. Scan daily_prices for drops > 15% (Adjustable threshold).
2. Distinguish:
   - "Bad Tick" (Flash Crash): Price recovers > 85% of the drop within 2 days.
   - "Split/Crash": Price remains low.
3. For Splits/Crashes:
   - Check if a corresponding Dividend record exists in DuckDB.
   - If missing, flag as "Missing Split".

Usage:
    uv run python scripts/ops/verify_splits_all.py
"""

import duckdb
import pandas as pd
import sys
import os

# Connect to DB
conn = duckdb.connect('data/market.duckdb', read_only=True)

THRESHOLD = -0.15

print(f"Scanning for drops < {THRESHOLD*100}% across 2000-2025...")

# Get all drops > 15%
q = """
WITH analysis AS (
    SELECT 
        stock_id, date, close,
        LAG(close) OVER (PARTITION BY stock_id ORDER BY date) as prev_close,
        LEAD(close) OVER (PARTITION BY stock_id ORDER BY date) as next_close,
        LEAD(close, 2) OVER (PARTITION BY stock_id ORDER BY date) as next_close_2
    FROM daily_prices
)
SELECT * FROM analysis
WHERE (close - prev_close) / prev_close < -0.15
ORDER BY date
"""

print("Executing SQL query...")
df = conn.execute(q).df()
print(f"Found {len(df)} potential large drops.")

missing_splits = []
bad_ticks = []

for idx, row in df.iterrows():
    stock_id = row['stock_id']
    date = pd.to_datetime(row['date'])
    dropped_price = row['close']
    prev_price = row['prev_close']
    next_price = row['next_close']
    next_price_2 = row['next_close_2']
    
    if pd.isna(prev_price) or prev_price == 0:
        continue
        
    # Calc Drop Percentage
    pct_drop = (dropped_price - prev_price) / prev_price
    
    # Check Rebound (Bad Tick detection)
    # Target: recover to at least 85% of previous price
    rebound_target = prev_price * 0.85 
    
    is_bad_tick = False
    if pd.notna(next_price) and next_price > rebound_target:
        is_bad_tick = True
    elif pd.notna(next_price_2) and next_price_2 > rebound_target:
        is_bad_tick = True
        
    if is_bad_tick:
        bad_ticks.append({
            'stock_id': stock_id,
            'date': date.strftime('%Y-%m-%d'),
            'drop_pct': pct_drop,
            'prev': prev_price,
            'curr': dropped_price,
            'next': next_price
        })
        continue

    # It's a persistent drop (Split or Crash)
    # Check if dividend record exists for this year
    # We query individually for simplicity (could join, but row count is small)
    has_div = conn.execute(f"SELECT 1 FROM dividends WHERE stock_id='{stock_id}' AND year={date.year}").fetchone()
    
    if not has_div:
        # Implied Split Ratio
        if dropped_price > 0:
            ratio = prev_price / dropped_price
            stock_div = (ratio - 1.0) # pure ratio
        else:
            ratio = 0
            stock_div = 0
            
        missing_splits.append({
            'stock_id': stock_id,
            'date': date.strftime('%Y-%m-%d'),
            'drop_pct': pct_drop,
            'prev': prev_price,
            'curr': dropped_price,
            'implied_ratio': ratio,
            'est_stock_div': stock_div
        })

print(f"\n=== BAD TICKS ({len(bad_ticks)}) - Recommendation: Delete Row ===")
for b in bad_ticks[:20]:
    print(f"{b['stock_id']} {b['date']}: {b['prev']:.2f} -> {b['curr']:.2f} ({b['drop_pct']*100:.1f}%) -> {b['next']} (Rebound)")

print(f"\n=== MISSING SPLITS ({len(missing_splits)}) - Recommendation: Insert Dividend ===")
for m in missing_splits[:50]:
    print(f"{m['stock_id']} {m['date']}: {m['prev']:.2f} -> {m['curr']:.2f} ({m['drop_pct']*100:.1f}%) | Ratio {m['implied_ratio']:.2f}")

# Save to CSV
os.makedirs('tests/analysis', exist_ok=True)
pd.DataFrame(bad_ticks).to_csv('tests/analysis/bad_ticks.csv', index=False)
pd.DataFrame(missing_splits).to_csv('tests/analysis/missing_splits_all.csv', index=False)
print(f"\nSaved analysis to tests/analysis/bad_ticks.csv and tests/analysis/missing_splits_all.csv")
