import pandas as pd
import os

f_golden = "/home/terwu01/github/martian/references/stock_list_s2006e2025_filtered.xlsx"
f_my = "project_tw/output/stock_list_s2006e2025_filtered.xlsx"

try:
    print("--- Golden Reference (6664) ---")
    if os.path.exists(f_golden):
        df_gold = pd.read_excel(f_golden)
        # Golden might use 'id' or 'stock_code'
        col_gold = 'id' if 'id' in df_gold.columns else 'stock_code'
        row_gold = df_gold[df_gold[col_gold].astype(str) == "6664"]
        if not row_gold.empty:
            print(row_gold.iloc[0].to_dict())
        else:
            print("Not found in Golden Reference.")
    else:
        print("Golden Reference file not found.")

    if os.path.exists(f_golden):
        # Debug columns
        if row_gold.empty:
            print(f"Columns in Golden: {df_gold.columns.tolist()}")


    print("\n--- My Output (6664) ---")
    if os.path.exists(f_my):
        df_my = pd.read_excel(f_my)
        col_my = 'id' if 'id' in df_my.columns else 'stock_code'
        row_my = df_my[df_my[col_my].astype(str) == "6664"]
        if not row_my.empty:
            print(row_my.iloc[0].to_dict())
        else:
            print("Not found in My Output.")
    else:
        print("My Output file not found.")

except Exception as e:
    print(f"Error: {e}")
