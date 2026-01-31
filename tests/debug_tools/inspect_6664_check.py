import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd

# Load both files
f_filtered = "project_tw/output/stock_list_s2006e2025_filtered.xlsx"
f_unfiltered = "project_tw/output/stock_list_s2006e2025_unfiltered.xlsx"

try:
    df_filt = pd.read_excel(f_filtered)
    # Check column names
    col = 'id' if 'id' in df_filt.columns else 'stock_code'
    
    row_filt = df_filt[df_filt[col].astype(str) == "6664"]
    print("--- Filtered Output (6664) ---")
    if not row_filt.empty:
        print(row_filt.iloc[0].to_dict())
    else:
        print("Not found in Filtered.")

    df_unfilt = pd.read_excel(f_unfiltered)
    row_unfilt = df_unfilt[df_unfilt[col].astype(str) == "6664"]
    print("\n--- Unfiltered Output (6664) ---")
    if not row_unfilt.empty:
        print(row_unfilt.iloc[0].to_dict())
    else:
        print("Not found in Unfiltered.")

except Exception as e:
    print(f"Error: {e}")
