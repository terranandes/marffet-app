import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import os

target_id = "6640"
out_dir = "project_tw/output"

files = {
    "Filtered": os.path.join(out_dir, "stock_list_s2006e2025_filtered.xlsx"),
    "Unfiltered": os.path.join(out_dir, "stock_list_s2006e2025_unfiltered.xlsx")
}

for name, path in files.items():
    if os.path.exists(path):
        print(f"\n--- {name} List ({path}) ---")
        df = pd.read_excel(path)
        # Ensure ID is string
        df['id'] = df['id'].astype(str)
        row = df[df['id'] == target_id]
        
        if not row.empty:
            print("Found!")
            # Print all columns that have non-null values or key metrics
            cols = ['id', 'name', 'id_name_yrs', 'valid_years', 'cagr_pct', 'cagr_std', 'volatility_pct']
            # Add yearly bao columns if exist
            bao_cols = [c for c in df.columns if 'bao' in c and row.iloc[0][c] != 0 and pd.notna(row.iloc[0][c])]
            
            print(row[cols + bao_cols[-10:]].iloc[0].to_string())
        else:
            print("Not Found.")
    else:
        print(f"File not found: {path}")
