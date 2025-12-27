
import pandas as pd
import os

files = [
    "sizeBytes/references/stock_list_s2006e2025_filtered.xlsx", 
    "references/stock_list_s2006e2025_unfiltered.xlsx",
    "references/CB6533.xlsx"
]

files = [os.path.abspath(f) for f in ["references/stock_list_s2006e2025_filtered.xlsx", "references/stock_list_s2006e2025_unfiltered.xlsx", "references/CB6533.xlsx"]]

for f in files:
    print(f"\n--- Inspecting {os.path.basename(f)} ---")
    try:
        df = pd.read_excel(f)
        print("Columns:", list(df.columns))
        print("Shape:", df.shape)
        print("First 2 rows:")
        print(df.head(2).to_markdown(index=False))
    except Exception as e:
        print(f"Error reading {f}: {e}")
