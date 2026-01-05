import json
import os
import pandas as pd

def check_6640():
    print("--- Checking 6640 (TPEx) ---")
    
    # 1. Check Raw Cache (TPEx)
    # 6640 is TPEx. Check recent year.
    found_in_cache = False
    for y in range(2023, 2026):
        fname = f"data/raw/TPEx_Market_{y}_Prices.json"
        if os.path.exists(fname):
            with open(fname) as f:
                d = json.load(f)
                if '6640' in d:
                    print(f"Found 6640 in {y} TPEx Cache: {d['6640']}")
                    found_in_cache = True
                else:
                    # print(f"Not in {y} TPEx Cache")
                    pass
    
    if not found_in_cache:
        print("6640 NOT found in any recent TPEx Cache.")

    # 2. Check Unfiltered Excel
    u_path = "project_tw/output/stock_list_s2006e2025_unfiltered.xlsx"
    if os.path.exists(u_path):
        try:
            df = pd.read_excel(u_path, dtype={'stock_code': str})
            row = df[df['stock_code'] == '6640']
            if not row.empty:
                print("\n--- Found in Unfiltered ---")
                print(row[['stock_code', 'stock_name', 'cagr_pct', 'volatility_pct', 'valid_lasting_years']].to_string())
            else:
                print("\nNOT found in Unfiltered Excel.")
        except Exception as e:
            print(f"Error reading Unfiltered Excel: {e}")

    # 3. Check Filtered Excel
    f_path = "project_tw/output/stock_list_s2006e2025_filtered.xlsx"
    if os.path.exists(f_path):
        try:
            df = pd.read_excel(f_path, dtype={'stock_code': str})
            row = df[df['stock_code'] == '6640']
            if not row.empty:
                print("\n--- Found in Filtered ---")
                print(row[['stock_code', 'stock_name']].to_string())
            else:
                print("\nNOT found in Filtered Excel.")
        except:
             pass

if __name__ == "__main__":
    check_6640()
