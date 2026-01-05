import pandas as pd
import os
import time

paths = [
    'project_tw/output/stock_list_s2006e2025_filtered.xlsx',
    'project_tw/output/stock_list_s2006e2025_unfiltered.xlsx'
]

for path in paths:
    print(f"--- Checking {path} ---")
    if os.path.exists(path):
        try:
            df = pd.read_excel(path)
            print("COLUMNS:", df.columns.tolist())
            if not df.empty:
                print("SAMPLE ROW:", df.iloc[0].to_dict())
                if 'id_name_yrs' in df.columns:
                    print(f"id_name_yrs Sample: {df.iloc[0]['id_name_yrs']}")
                if 'valid_years' in df.columns:
                    print(f"valid_years Sample: {df.iloc[0]['valid_years']}")
        except Exception as e:
            print("Error reading:", e)
    else:
        print("File not found.")
