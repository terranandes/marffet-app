import pandas as pd
import os

ref_path = "project_tw/references/stock_list_s2006e2025_filtered.xlsx"

if not os.path.exists(ref_path):
    # Try alternate path if not found (based on list_dir earlier)
    # Earlier list_dir output: {"name":"stock_list_s2006e2025_filtered.xlsx", ...} in "project_tw/references/"?
    # No, tool call 311 was list_dir "martian/references".
    # But user prompt said "~/github/martian/references/..."
    ref_path = "references/stock_list_s2006e2025_filtered.xlsx"

if os.path.exists(ref_path):
    print(f"Inspecting {ref_path}...")
    try:
        df = pd.read_excel(ref_path)
        print("Columns:", df.columns.tolist())
        print("Shape:", df.shape)
        print("\nFirst 3 rows:")
        print(df.head(3).to_string())
        
        # Check specific column 'id_name_yrs' mentioned in previous conversation
        if 'id_name_yrs' in df.columns:
            print("\nSample 'id_name_yrs':", df['id_name_yrs'].head(3).values)
    except Exception as e:
        print(f"Error reading Excel: {e}")
else:
    print(f"File not found: {ref_path}")
