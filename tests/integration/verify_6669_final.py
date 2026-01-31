import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
import os

def check_verification():
    print("--- 6669 Final Verification ---")
    
    # 1. Check Cache Data (Should be preserved/updated)
    p_file = "data/raw/Market_2019_Prices.json"
    if os.path.exists(p_file):
        with open(p_file) as f:
            d = json.load(f).get('6669', {})
            print(f"Price 2019: {d}")
            
    d_file = "data/raw/TWT49U_2019.json"
    if os.path.exists(d_file):
        with open(d_file) as f:
            full = json.load(f)
            rows = full.get('data', [])
            found = [r for r in rows if '6669' in str(r)]
            print(f"Div 2019: {found}")

    # 2. Check Output Excel (Optional, but hard to parse xlsx in script without openpyxl deps installed? 
    # venv has pandas, so should have openpyxl usually if using to_excel)
    # Let's try reading the output excel using pandas.
    
    excel_path = "project_tw/output/stock_list_s2006e2025_filtered.xlsx"
    if os.path.exists(excel_path):
        import pandas as pd
        try:
            df = pd.read_excel(excel_path)
            row = df[df['stock_code'] == 6669] # Or '6669' string?
            if row.empty:
                row = df[df['stock_code'] == '6669']
            
            if not row.empty:
                print("\n--- Excel Output ---")
                print(row[['stock_code', 'stock_name', 'cagr_pct', 's2006e2025bao']].to_string())
            else:
                print("6669 not found in filtered list (maybe filtered out?)")
                # Check unfiltered
                u_path = "project_tw/output/stock_list_s2006e2025_unfiltered.xlsx"
                if os.path.exists(u_path):
                     dfu = pd.read_excel(u_path)
                     rowu = dfu[dfu['stock_code'] == '6669']
                     if not rowu.empty:
                         print("\n--- Unfiltered Excel Output ---")
                         print(rowu[['stock_code', 'cagr_pct', 's2006e2025bao']].to_string())
        except Exception as e:
            print(f"Could not read excel: {e}")

if __name__ == "__main__":
    check_verification()
