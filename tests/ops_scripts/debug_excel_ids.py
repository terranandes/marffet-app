import pandas as pd
import os

base_path = "app/project_tw/references/"
file_unfiltered = os.path.join(base_path, "stock_list_s2010e2026_unfiltered.xlsx")
file_filtered = os.path.join(base_path, "stock_list_s2010e2026_filtered.xlsx")

def debug_ids():
    print("Loading Excel files for debug...")
    df_u = pd.read_excel(file_unfiltered)
    df_f = pd.read_excel(file_filtered)
    
    print("\n--- Unfiltered IDs (Head) ---")
    print(df_u['id'].head(10).tolist())
    print("\n--- Filtered IDs (Head) ---")
    print(df_f['id'].head(10).tolist())

    print("\n--- Unfiltered IDs (Tail) ---")
    print(df_u['id'].tail(10).tolist())

if __name__ == "__main__":
    debug_ids()
