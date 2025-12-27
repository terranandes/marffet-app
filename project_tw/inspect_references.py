import pandas as pd
import os

REFERENCES_DIR = "/home/terwu01/github/martian/references"

def inspect_excel(filename):
    path = os.path.join(REFERENCES_DIR, filename)
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return

    print(f"\n🔍 Inspecting: {filename}")
    try:
        # Load just headers first to be fast, or small sample
        df = pd.read_excel(path, nrows=5)
        print(f"   Columns ({len(df.columns)}): {list(df.columns)}")
        print("   Sample Data (First 2 rows):")
        print(df.head(2).to_string())
        
        # Check basic stats if possible?
        # print(df.dtypes)
    except Exception as e:
        print(f"   ⚠️ Error reading file: {e}")

def main():
    files_to_check = [
        "stock_list_s2006e2025_unfiltered.xlsx",
        "stock_list_s2006e2025_filtered.xlsx",
        "CB6533.xlsx"
    ]
    
    for f in files_to_check:
        inspect_excel(f)

if __name__ == "__main__":
    main()
