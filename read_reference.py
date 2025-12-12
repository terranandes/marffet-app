import pandas as pd

def read_ref():
    file_path = '/home/terwu01/github/martian/references/stock_list_s2006e2025_filtered.xlsx'
    print(f"Reading {file_path}...")
    try:
        df = pd.read_excel(file_path)
        # Find 2330
        # Columns might be 'id', 'name', 's2006e2007bao', etc.
        # Check explicit columns
        tsmc = df[df['id'] == 2330] # ID might be int or str
        if tsmc.empty:
             tsmc = df[df['id'] == '2330']
             
        if not tsmc.empty:
            print("--- Reference TSMC Data ---")
            # Print all s2006e...bao columns
            for col in df.columns:
                if col.startswith('s2006') and col.endswith('bao'):
                    val = tsmc.iloc[0][col]
                    print(f"{col}: {val}")
        else:
            print("TSMC not found in reference.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_ref()
