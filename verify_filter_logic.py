import pandas as pd
import os

def verify_filters():
    path = "project_tw/output/stock_list_s2006e2025_filtered.xlsx"
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return
        
    df = pd.read_excel(path)
    print(f"Loaded Filtered List. Rows: {len(df)}")
    
    if df.empty:
        print("Error: Filtered list is empty!")
        return

    # Check Columns
    print(f"Columns: {df.columns.tolist()}")
    if 'valid_years' not in df.columns:
        print("Error: Missing 'valid_years' column.")

    # 1. Check Volatility (Approx)
    # Find TSMC in unfiltered list? Or assume filtered list is correct.
    # Max volatility should be close to TSMC's (e.g. 20-30%).
    max_vol = df['volatility_pct'].max()
    print(f"Max Volatility in Filtered List: {max_vol:.2f}%")
    
    # 2. Check Exclusions
    # Leverage
    lev_etfs = df[df['id'].astype(str).str.endswith('L')]
    if not lev_etfs.empty:
        print(f"Error: Found Leverage ETFs: {lev_etfs['id'].tolist()}")
    else:
        print("Pass: No Leverage ETFs found.")
        
    # DRs (Start 91, len 4)
    drs = df[df['id'].astype(str).str.startswith('91') & (df['id'].astype(str).str.len() == 4)]
    if not drs.empty:
        print(f"Error: Found DRs: {drs['id'].tolist()}")
    else:
        print("Pass: No DRs found.")
        
    # Warrants (Len 6, start 03-08)
    warrants = df[
        (df['id'].astype(str).str.len() == 6) & 
        (df['id'].astype(str).str.startswith(('03','04','05','06','07','08')))
    ]
    if not warrants.empty:
        print(f"Error: Found Warrants: {warrants['id'].tolist()}")
    else:
        print("Pass: No Warrants found.")
        
    # Valid Years > 3
    short_life = df[df['valid_years'] <= 3]
    if not short_life.empty:
         print(f"Error: Found items with <= 3 years: {short_life['id'].tolist()}")
    else:
         print("Pass: All items have > 3 years.")

if __name__ == "__main__":
    verify_filters()
