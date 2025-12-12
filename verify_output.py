import pandas as pd
import os

def verify():
    path = "project_tw/output/stock_list_s2006e2025_unfiltered.xlsx"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    df = pd.read_excel(path)
    print(f"Loaded Excel. Rows: {len(df)}")
    
    # Expanded List (14 items) - Excluded 65331 (Unsupported)
    target_list = [
        '00937B', '00953B', '00933B', '00950B', '00945B', 
        '00980D', '00894', '00981A', '00983A', '00830', 
        '009811', '00927', '00878', '00919'
    ]
    
    found_count = 0
    missing = []
    
    print(f"Checking {len(target_list)} targets...")
    
    if 'id' in df.columns:
        # Normalize to string
        df['id'] = df['id'].astype(str)
        
        for t in target_list:
            row = df[df['id'] == t]
            if not row.empty:
                 print(f"[FOUND] {t}")
                 found_count += 1
                 # Optional: Print basic info to confirm stats
                 print(row.iloc[0].to_dict())
            else:
                 print(f"[MISSING] {t}")
                 missing.append(t)
                 
    print(f"\nSummary: Found {found_count}/{len(target_list)}")
    if missing:
        print(f"Missing Codes: {missing}")
             
    # Check total count
    print(f"Total Unique IDs: {df['id'].nunique()}")

if __name__ == "__main__":
    verify()
