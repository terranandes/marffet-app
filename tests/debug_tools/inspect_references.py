import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import os

REF_DIR = "references"
FILES = [
    "stock_list_s2006e2025_unfiltered.xlsx",
    "stock_list_s2006e2025_filtered.xlsx",
    "CB6533.xlsx"
]

def inspect_ref():
    for f in FILES:
        path = os.path.join(REF_DIR, f)
        if not os.path.exists(path):
            print(f"[MISSING] {path}")
            continue
            
        print(f"\n=== Inspecting {f} ===")
        try:
            df = pd.read_excel(path)
            print(f"Shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            
            # Check for critical columns mentioned in previous verify steps
            if 'id' in df.columns:
                print(f"Unique IDs: {df['id'].nunique()}")
                
        except Exception as e:
            print(f"Error reading {f}: {e}")

if __name__ == "__main__":
    inspect_ref()
