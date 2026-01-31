import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import os

files = [
    "references/stock_list_s2006e2025_unfiltered.xlsx",
    "references/stock_list_s2006e2025_filtered.xlsx",
    "references/CB6533.xlsx"
]

for f in files:
    print(f"--- Inspecting {f} ---")
    if not os.path.exists(f):
        print("File not found.")
        continue
    
    try:
        df = pd.read_excel(f, nrows=5)
        print("Columns:", list(df.columns))
        print("First row:", df.iloc[0].to_dict())
        print("Types:", df.dtypes.to_dict())
    except Exception as e:
        print(f"Error reading {f}: {e}")
    print("\n")
