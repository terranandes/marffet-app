import pandas as pd
import os

base_path = "app/project_tw/references/"
file_unfiltered = os.path.join(base_path, "stock_list_s2010e2026_unfiltered.xlsx")
file_filtered = os.path.join(base_path, "stock_list_s2010e2026_filtered.xlsx")

def inspect_excel(filepath):
    print(f"--- Inspecting {filepath} ---")
    try:
        df = pd.read_excel(filepath)
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print("First 3 rows:")
        print(df.head(3).to_markdown(index=False))
        return df
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

df_u = inspect_excel(file_unfiltered)
print("\n")
df_f = inspect_excel(file_filtered)
