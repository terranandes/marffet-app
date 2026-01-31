import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import os

def check():
    f = "project_tw/output/stock_list_s2006e2025_filtered.xlsx"
    if not os.path.exists(f):
        print(f"File not found: {f}")
        return
    
    df = pd.read_excel(f)
    print(f"Loaded {len(df)} rows.")
    
    # Check 0050
    # Column 'id' or 'stock_code'?
    # Run analysis changed columns to 'id', 'name', 'valid_years', 's2006e2025bao'
    
    row = df[df['id'].astype(str) == '0050']
    if row.empty:
        print("0050 not found in filtered list!")
        # Check unfiltered?
        f_un = "project_tw/output/stock_list_s2006e2025_unfiltered.xlsx"
        if os.path.exists(f_un):
            df_un = pd.read_excel(f_un)
            r2 = df_un[df_un['id'].astype(str) == '0050']
            if not r2.empty:
                print(f"Found 0050 in UNFILTERED: {r2.iloc[0].to_dict()}")
            else:
                print("0050 not found in Unfiltered either!")
    else:
        print("Found 0050 in FILTERED:")
        data = row.iloc[0].to_dict()
        print(f"CAGR (s2006e2025bao): {data.get('s2006e2025bao')}")
        print(f"Full Row: {data}")

if __name__ == "__main__":
    check()
