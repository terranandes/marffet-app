import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import os

REF_PATH = "references/stock_list_s2006e2025_unfiltered.xlsx"
CURR_PATH = "project_tw/output/stock_list_s2006e2025_unfiltered.xlsx"

def compare():
    print("=== Correlation Check: Current vs Golden ===")
    
    if not os.path.exists(REF_PATH):
        print("Ref missing")
        return
    if not os.path.exists(CURR_PATH):
        print("Current output missing")
        return

    ref_df = pd.read_excel(REF_PATH)
    curr_df = pd.read_excel(CURR_PATH)
    
    print(f"Ref Shape: {ref_df.shape}")
    print(f"Curr Shape: {curr_df.shape}")
    
    # Check Column Overlap
    ref_cols = set(ref_df.columns)
    curr_cols = set(curr_df.columns)
    
    missing_cols = ref_cols - curr_cols
    extra_cols = curr_cols - ref_cols
    
    print(f"\nMissing Columns in Current ({len(missing_cols)}):")
    print(list(missing_cols)[:10], "..." if len(missing_cols)>10 else "")
    
    print(f"\nExtra Columns in Current ({len(extra_cols)}):")
    print(list(extra_cols)[:10], "..." if len(extra_cols)>10 else "")
    
    # Check ID overlap
    if 'id' in ref_df.columns and 'id' in curr_df.columns:
        ref_ids = set(ref_df['id'].astype(str))
        curr_ids = set(curr_df['id'].astype(str))
        
        missing_ids = ref_ids - curr_ids
        print(f"\nMissing IDs in Current ({len(missing_ids)}):")
        print(list(missing_ids)[:10], "...")

if __name__ == "__main__":
    compare()
