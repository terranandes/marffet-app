import pandas as pd

def verify():
    # Load Unfiltered to get stats
    try:
        df_unf = pd.read_excel('project_tw/output/stock_list_s2006e2025_unfiltered.xlsx')
        df_unf['id'] = df_unf['id'].astype(str)
        
        row_3147 = df_unf[df_unf['id'] == '3147']
        row_2330 = df_unf[df_unf['id'] == '2330']
        
        print("--- Benchmark TSMC (2330) ---")
        if not row_2330.empty:
            print(row_2330[['id', 'name', 'cagr_pct', 'volatility_pct', 'cagr_std']].to_string())
        
        print("\n--- Target 3147 (Da Zong) ---")
        if not row_3147.empty:
            print(row_3147[['id', 'name', 'cagr_pct', 'volatility_pct', 'cagr_std']].to_string())
        else:
            print("3147 Not Found in Unfiltered.")

        # Check Filtered
        df_fil = pd.read_excel('project_tw/output/stock_list_s2006e2025_filtered.xlsx')
        df_fil['id'] = df_fil['id'].astype(str)
        is_in_filtered = not df_fil[df_fil['id'] == '3147'].empty
        
        print(f"\nIs 3147 in Filtered List? {is_in_filtered}")
        
    except Exception as e:
        print(f"Error: {e}")

verify()
