import pandas as pd
import os

# Paths
base_dir = os.getcwd()
our_list_path = os.path.join(base_dir, "app/project_tw/stock_list.csv")
golden_excel_path = os.path.join(base_dir, "app/project_tw/references/stock_list_s2010e2026_filtered.xlsx")

def clean_id(val):
    """Convert value to 4-digit string ID."""
    try:
        s = str(int(float(val)))
        return s.zfill(4)
    except:
        return str(val).strip()

def verify_universe():
    print("--- Stock Universe Verification Report ---")
    
    # 1. Load Our List (ISIN Source)
    print(f"Loading Our Engine List: {our_list_path}")
    if not os.path.exists(our_list_path):
        print("ERROR: app/project_tw/stock_list.csv not found.")
        return

    df_ours = pd.read_csv(our_list_path, dtype={'code': str, 'name': str})
    our_ids = set(df_ours['code'].str.strip())
    print(f"Our Count: {len(our_ids)}")

    # 2. Load Golden List (MoneyCome Filtered)
    print(f"Loading Golden Answer: {golden_excel_path}")
    if not os.path.exists(golden_excel_path):
        print("ERROR: Golden Excel file not found.")
        return

    df_golden = pd.read_excel(golden_excel_path)
    df_golden['clean_id'] = df_golden['id'].apply(clean_id)
    golden_ids = set(df_golden['clean_id'])
    print(f"Golden Count: {len(golden_ids)}")

    # 3. Apply Engine Logic (Simulation)
    # Filter our list to "Valid Candidates"
    # Rule: 
    # - Exclude Warrants (Name contains "購")
    # - Exclude CBs (Convertible Bonds) - usually 5 digits ending in number? Or Market Type 'Bond'?
    # - Exclude 6-digit codes unless they look like ETFs? 
    # Let's inspect "Extra" to refine.
    # Warrants usually 6 chars.
    
    engine_filtered_ids = set()
    for _, row in df_ours.iterrows():
        code = str(row['code']).strip()
        name = str(row['name']).strip()
        mkt = str(row['market_type'])
        
        # Filter Logic
        if mkt == 'Bond': continue
        if len(code) == 6 and (code.startswith('03') or code.startswith('04') or code.startswith('05') or code.startswith('06') or code.startswith('07') or code.startswith('08') or code.startswith('7')): 
             # Likely Warrants (03-08, 7x). 
             # But check name for "購"
             if '購' in name: continue
             if '牛' in name: continue
             if '熊' in name: continue
             
        # Also filter "Rights" (entitlements)?
        
        engine_filtered_ids.add(code)

    print(f"Engine Filtered Count: {len(engine_filtered_ids)}")

    # 4. Compare
    common = engine_filtered_ids.intersection(golden_ids)
    missing_in_ours = golden_ids - engine_filtered_ids # False Negatives
    extra_in_ours = engine_filtered_ids - golden_ids   # False Positives

    print("\n--- Comparison Results ---")
    print(f"Match Count: {len(common)}")
    print(f"Missing from Ours (In Golden but not Engine): {len(missing_in_ours)}")
    print(f"Extra in Ours (In Engine but not Golden):   {len(extra_in_ours)}")

    # 5. Analyze Discrepancies
    if missing_in_ours:
        print("\n[CRITICAL] Stocks in Golden Answer but MISSING from Our Engine:")
        missing_sample = list(missing_in_ours)
        missing_sample.sort()
        # Print all if small enough
        if len(missing_sample) < 100:
             # Get names from df_golden
             res = df_golden[df_golden['clean_id'].isin(missing_sample)][['clean_id', 'name']]
             print(res.to_string(index=False))
        else:
             print(f"(First 20 of {len(missing_sample)})")
             print(missing_sample[:20])

    if extra_in_ours:
        print("\n[INFO] Stocks in Our Engine but NOT in Golden Answer:")
        extra_sample = list(extra_in_ours)[:20]
        extra_df = df_ours[df_ours['code'].isin(extra_sample)]
        print(extra_df[['code', 'name', 'industry', 'market_type']].to_string(index=False))
        
        print("\n--- Top Industries of Extra ---")
        print(df_ours[df_ours['code'].isin(extra_in_ours)]['industry'].value_counts().head(10))

if __name__ == "__main__":
    verify_universe()
