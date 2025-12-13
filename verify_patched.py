import pandas as pd

def verify_patched():
    path = 'project_tw/output/stock_list_s2006e2025_unfiltered.xlsx'
    try:
        df = pd.read_excel(path)
        df['id'] = df['id'].astype(str)
        
        # 1. Check L
        l_stocks = df[df['id'].str.endswith('L')]
        print(f"Leveraged Stocks Remaining: {len(l_stocks)}")

        # 2. Check Names from Screenshot
        # 6498, 6720, 3017, 5314, 3147, 3363, 6442?, 5274, 6640
        targets = ['6498', '6720', '3017', '5314', '3147', '3363', '5274', '6640']
        print(f"\nChecking Names for {targets}...")
        for t in targets:
            row = df[df['id'] == t]
            if not row.empty:
                print(f"{t}: {row.iloc[0]['name']}")
            else:
                print(f"{t}: Not Found")
                
        # Count Unknowns
        unknowns = df[df['name'] == 'Unknown']
        print(f"\nTotal Unknown Names: {len(unknowns)}")
        if not unknowns.empty:
            print("Sample Unknowns:", unknowns['id'].head().tolist())
        else:
            print("All names resolved!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_patched()
