
import json
import pandas as pd
from pathlib import Path

def main():
    # 1. Load Our Verification Data
    json_path = Path("output/universal_verification.json")
    if not json_path.exists():
        print("Error: universal_verification.json not found")
        return

    with open(json_path, "r") as f:
        root_data = json.load(f)
        our_data = root_data.get('all_results', [])
    
    # Convert to Dict for easy lookup: ID -> CAGR
    our_cagr = {}
    for item in our_data:
        try:
            sid = str(item.get("stock_id"))
            cagr = item.get("cagr")
            if sid and cagr is not None:
                our_cagr[sid] = float(cagr)
        except:
            pass

    # 2. Load MoneyCome Excel
    excel_path = Path("app/project_tw/references/stock_list_s2006e2026_unfiltered.xlsx")
    if not excel_path.exists():
        print(f"Error: Excel not found at {excel_path}")
        return

    print(f"Loading Excel from {excel_path}...")
    df = pd.read_excel(excel_path)
    
    # Expected columns: 'Symbol', 'CAGR' (or similar). Let's peek if columns differ.
    # Assuming 'Symbol' and 'CAGR' based on previous context.
    # If column names are different, this might fail, so I'll print them first if needed.
    # But let's assume standard names or try to detect.
    
    # Clean column names
    df.columns = df.columns.astype(str).str.strip().str.lower()
    
    # Identify columns
    symbol_col = 'id'
    cagr_col = 's2006e2026bao'

    if symbol_col not in df.columns or cagr_col not in df.columns:
        print(f"Error: Required columns not found. Need 'id' and 's2006e2026bao'. Found: {df.columns.tolist()[:10]}...")
        return

    print(f"Using columns: Symbol='{symbol_col}', CAGR='{cagr_col}'")
    
    # Debug: Print sample IDs
    print(f"Sample Our IDs: {list(our_cagr.keys())[:5]}")
    print(f"Sample Excel IDs: {df[symbol_col].head().tolist()}")

    # 3. Compare
    comparison = []
    
    print("\n--- Key Stock Comparison ---")
    targets = ['0050', '2330', '0056', '2317', '2454']
    
    for _, row in df.iterrows():
        # Force string conversion and clean
        val = row[symbol_col]
        if pd.isna(val): continue
        sid = str(int(val)) if isinstance(val, float) else str(val).split('.')[0].strip()
        
        try:
            mc_cagr = float(row[cagr_col].replace('%', '')) if isinstance(row[cagr_col], str) else float(row[cagr_col])
        except:
            continue # Skip invalid data

        our_val = our_cagr.get(sid)
        
        if our_val is not None:
            diff = our_val - mc_cagr
            comparison.append({
                'id': sid,
                'name': row.get('Name', row.get('名稱', '')),
                'our_cagr': our_val,
                'mc_cagr': mc_cagr,
                'diff': diff,
                'abs_diff': abs(diff)
            })
            
            if sid in targets:
                print(f"[{sid}] Our: {our_val:.2f}% | MC: {mc_cagr:.2f}% | Diff: {diff:+.2f}%")

    # 4. Overall Stats
    df_comp = pd.DataFrame(comparison)
    if df_comp.empty:
        print("No matches found!")
        return

    print("\n--- Overall Statistics ---")
    print(f"Total Matched: {len(df_comp)}")
    print(f"Within 1% Diff: {len(df_comp[df_comp['abs_diff'] < 1])}")
    print(f"Within 2% Diff: {len(df_comp[df_comp['abs_diff'] < 2])}")
    print(f"Mean Abs Diff: {df_comp['abs_diff'].mean():.2f}%")
    
    print("\n--- Top 10 Largest Discrepancies (Our > MC) ---")
    print(df_comp.sort_values('diff', ascending=False).head(10)[['id', 'our_cagr', 'mc_cagr', 'diff']].to_string(index=False))

    print("\n--- Top 10 Largest Discrepancies (Our < MC) ---")
    # Filter out -100s (missing data) to see real discrepancies
    real_diffs = df_comp[df_comp['our_cagr'] > -90]
    print(real_diffs.sort_values('diff', ascending=True).head(10)[['id', 'our_cagr', 'mc_cagr', 'diff']].to_string(index=False))

if __name__ == "__main__":
    main()
