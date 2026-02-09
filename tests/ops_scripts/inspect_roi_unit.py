import pandas as pd
import os

base_path = "app/project_tw/references/"
file_filtered = os.path.join(base_path, "stock_list_s2010e2026_filtered.xlsx")

def inspect_tsmc():
    print(f"Loading {file_filtered}...")
    df = pd.read_excel(file_filtered)
    
    # Find 2330
    # ID might be float 2330.0 or string "2330"
    # Create clean_id
    df['clean_id'] = df['id'].apply(lambda x: str(int(float(x))).zfill(4) if pd.notna(x) and isinstance(x, (int, float)) else str(x).strip())
    
    target = df[df['clean_id'] == '2330']
    
    if not target.empty:
        print("--- TSMC (2330) Golden Data ---")
        # Print columns starting with 's2010'
        cols = [c for c in df.columns if c.startswith('s2010e2026')]
        print(target[['clean_id', 'name'] + cols].to_string())
        
        val = target.iloc[0]['s2010e2026bao']
        print(f"\nRaw ROI Value (s2010e2026bao): {val}")
        print(f"Type: {type(val)}")
    else:
        print("TSMC not found in filtered list!")

if __name__ == "__main__":
    inspect_tsmc()
