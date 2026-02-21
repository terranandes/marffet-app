"""
Supplement Missing Splits for ALL years (2000-2025).

Logic:
1. Load `tests/analysis/missing_splits_all.csv`.
2. For each row, INSERT INTO dividends (stock_id, year, stock, cash).
   - Cash = 0.0
   - Stock = (implied_ratio - 1.0) * 10
     Example: 4-for-1 split (Ratio 4.0) -> Stock Div 30.0?
     Wait.
     Stock Dividend 1.0 means +10% shares. Ratio 1.1.
     Stock Dividend 10.0 means +100% shares. Ratio 2.0.
     Stock Dividend X means Ratio = 1 + X/10.
     So X = (Ratio - 1) * 10.
     
     Example: 0050 Ratio 4.0 (188->47).
     X = (4 - 1) * 10 = 30.0.
     A 30.0 stock dividend? (3000 shares per 1000 shares held).
     Yes. 1000 -> 4000 shares.
     
   - Year = Year of the crash date.
   
3. Handling Conflicts:
   - If a record exists for (stock_id, year), UPDATE it?
   - Or just INSERT OR IGNORE?
   - The CSV generator `verify_splits_all.py` ALREADY checked that no dividend record exists.
   - So we can safe INSERT.

Usage:
    uv run python scripts/ops/supplement_splits.py --apply
"""

import duckdb
import pandas as pd
import argparse
import os
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.project_tw.calculator import EXOTIC_PARS

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Apply changes to DB')
    args = parser.parse_args()

    CSV_PATH = 'tests/analysis/missing_splits_all.csv'
    
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found. Run verify_splits_all.py first.")
        exit(1)

    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} missing splits to patch.")
    
    if df.empty:
        print("No splits to patch.")
        exit(0)

    # 0050 check
    mask_0050 = df['stock_id'] == '0050'
    if mask_0050.any():
        print("Found 0050 in patch list:")
        print(df[mask_0050])

    if not args.apply:
        print("\n[Preview Mode] Run with --apply to execute.")
        return

    conn = duckdb.connect('data/market.duckdb')
    
    print("\nApplying patches...")
    count = 0
    
    for _, row in df.iterrows():
        stock_id = row['stock_id']
        date_str = str(row['date'])
        year = int(date_str[:4])
        
        ratio = float(row['implied_ratio'])
        if ratio <= 1.0:
            print(f"Skipping invalid ratio {ratio} for {stock_id}")
            continue
            
        # Calculate Stock Dividend using EXACT Par Value
        par_value = EXOTIC_PARS.get(stock_id, 10.0)
        stock_div = (ratio - 1.0) * par_value
        
        # Cap/Sanity check
        if stock_div > 1000: # 100-for-1 split limit
            print(f"Skipping insane split {stock_id} (div {stock_div})")
            continue
            
        try:
            # Insert or Update
            # If record exists (e.g. Cash Div only), we UPDATE the stock column if it is 0.
            q = f"""
                INSERT INTO dividends (stock_id, year, cash, stock) 
                VALUES ('{stock_id}', {year}, 0.0, {stock_div:.2f})
                ON CONFLICT (stock_id, year) DO UPDATE 
                SET stock = EXCLUDED.stock
                WHERE dividends.stock = 0
            """
            conn.execute(q)
            count += 1
        except Exception as e:
            # Likely PK violation if generator loop was imperfect
            # We can try UPDATE if needed, but risky.
            print(f"Error patching {stock_id} {year}: {e}")

    print(f"Successfully patched {count} dividend records.")
    
    # Verify 0050
    if mask_0050.any():
        print("\nVerifying 0050 patch:")
        res = conn.execute("SELECT * FROM dividends WHERE stock_id='0050' ORDER BY year").fetchall()
        for r in res:
            print(r)

    conn.close()

if __name__ == "__main__":
    main()
