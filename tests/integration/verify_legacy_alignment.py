import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


import pandas as pd
import os

# Paths
new_filtered = 'project_tw/output/stock_list_s2006e2025_filtered.xlsx'
ref_filtered = 'references/stock_list_s2006e2025_filtered.xlsx'

new_unfiltered = 'project_tw/output/stock_list_s2006e2025_unfiltered.xlsx'
ref_unfiltered = 'references/stock_list_s2006e2025_unfiltered.xlsx'

def compare_files(new_path, ref_path, label):
    print(f"\n=== Comparing {label} ===")
    if not os.path.exists(new_path):
        print(f"MISSING NEW: {new_path}")
        return
    if not os.path.exists(ref_path):
        print(f"MISSING REF: {ref_path}")
        return
        
    try:
        df_new = pd.read_excel(new_path)
        df_ref = pd.read_excel(ref_path)
        
        # 1. Column Check
        cols_new = set(df_new.columns)
        cols_ref = set(df_ref.columns)
        
        missing_in_new = cols_ref - cols_new
        extra_in_new = cols_new - cols_ref
        
        print(f"Columns in Ref: {len(cols_ref)}")
        print(f"Columns in New: {len(cols_new)}")
        
        if missing_in_new:
            print(f"[WARN] Missing Columns in New: {missing_in_new}")
        else:
            print("[OK] All reference columns present.")
            
        if extra_in_new:
            print(f"[INFO] New columns added: {extra_in_new}")
            
        # 2. Row Count
        print(f"Rows New: {len(df_new)}")
        print(f"Rows Ref: {len(df_ref)}")
        
        # 3. Data Check (Sample)
        # Check TSMC (2330)
        def check_stock(code, col='cagr_pct'):
            # Convert ID to string for safety
            df_new['id'] = df_new['id'].astype(str)
            df_ref['id'] = df_ref['id'].astype(str)
            
            row_new = df_new[df_new['id'] == str(code)]
            row_ref = df_ref[df_ref['id'] == str(code)]
            
            if row_new.empty:
                print(f"[WARN] Stock {code} missing in NEW")
                return
            if row_ref.empty:
                print(f"[WARN] Stock {code} missing in REF")
                return
                
            val_new = row_new.iloc[0].get(col)
            val_ref = row_ref.iloc[0].get(col)
            
            print(f"Stock {code} [{col}]: New={val_new}, Ref={val_ref}")
            
            # Check s2006e2025bao
            # Or the LAST year column
            bao_cols = [c for c in df_ref.columns if 'bao' in c]
            if bao_cols:
                last_bao = bao_cols[-1]
                val_bao_new = row_new.iloc[0].get(last_bao)
                val_bao_ref = row_ref.iloc[0].get(last_bao)
                print(f"Stock {code} [{last_bao}]: New={val_bao_new}, Ref={val_bao_ref}")

        check_stock('2330') # TSMC
        check_stock('2317') # Foxconn
        
    except Exception as e:
        print(f"Error comparing: {e}")

compare_files(new_filtered, ref_filtered, "FILTERED")
compare_files(new_unfiltered, ref_unfiltered, "UNFILTERED")
