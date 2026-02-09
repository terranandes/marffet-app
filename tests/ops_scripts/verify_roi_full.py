import asyncio
import pandas as pd
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.project_tw.strategies.mars import MarsStrategy

# Paths
base_dir = os.getcwd()
file_filtered = os.path.join(base_dir, "app/project_tw/references/stock_list_s2010e2026_filtered.xlsx")
report_path = os.path.join(base_dir, "tests/evidence/roi_correlation.csv")

def clean_id(val):
    try:
        s = str(int(float(val)))
        return s.zfill(4)
    except:
        return str(val).strip()

async def main():
    print("--- ROI Correlation Verification (Full Batch) ---")
    
    # 1. Load Universe from Excel
    print(f"Loading Universe from {file_filtered}...")
    if not os.path.exists(file_filtered):
        print("Error: Excel file not found.")
        return

    df_gold = pd.read_excel(file_filtered)
    df_gold['clean_id'] = df_gold['id'].apply(lambda x: str(int(float(x))).zfill(4) if pd.notna(x) and isinstance(x, (int, float)) else str(x).strip())
    
    # Map ID -> Golden ROI
    # Check column name
    roi_col = 's2010e2026bao'
    if roi_col not in df_gold.columns:
        print(f"Error: Column {roi_col} not found in Excel.")
        print(f"Available columns: {list(df_gold.columns)}")
        return
        
    gold_map = {}
    for _, row in df_gold.iterrows():
        sid = row['clean_id']
        val = row[roi_col]
        gold_map[sid] = val

    all_ids = list(gold_map.keys())
    print(f"Target Universe: {len(all_ids)} stocks.")

    # 2. Run Engine
    print("Initializing MarsStrategy...")
    strategy = MarsStrategy()
    
    # Parameters
    start_year = 2010
    end_year = 2026
    
    print(f"Running Analysis for {start_year}-{end_year}...")
    
    # Callback for progress
    def progress(msg, pct=0):
        print(f"[Engine] {msg} ({pct}%)")

    results = await strategy.analyze_stock_batch(all_ids, start_year, end_year, status_callback=progress)
    
    print(f"Engine Analysis Complete. Got {len(results)} results.")

    # 3. Compare
    comparison = []
    
    for res in results:
        sid = res.get('stock_code')
        engine_cagr = res.get('cagr_pct', 0.0)
        gold_cagr = gold_map.get(sid, 0.0)
        
        # Handle NaN in gold
        if pd.isna(gold_cagr): gold_cagr = 0.0
        
        diff = engine_cagr - gold_cagr
        abs_diff = abs(diff)
        
        comparison.append({
            'code': sid,
            'name': res.get('stock_name', ''),
            'engine_cagr': round(engine_cagr, 2),
            'gold_cagr': round(gold_cagr, 2),
            'diff': round(diff, 2),
            'abs_diff': round(abs_diff, 2),
            'valid_years': res.get('valid_lasting_years', 0)
        })
        
    df_comp = pd.DataFrame(comparison)
    
    # Sort by Abs Diff desc
    df_comp.sort_values(by='abs_diff', ascending=False, inplace=True)
    
    # Save
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    df_comp.to_csv(report_path, index=False)
    print(f"\nReport saved to: {report_path}")
    
    # Summary Props
    match_count = len(df_comp[df_comp['abs_diff'] < 1.0]) # Within 1%
    total_count = len(df_comp)
    print(f"\n--- Summary ---")
    print(f"Total Compared: {total_count}")
    print(f"Perfect Matches (<1% diff): {match_count} ({match_count/total_count*100:.1f}%)")
    
    print("\n[Top 10 Discrepancies]")
    print(df_comp.head(10).to_string(index=False))

    print("\n[Top 10 Matches]")
    print(df_comp[df_comp['abs_diff'] < 0.1].head(10).to_string(index=False))

if __name__ == "__main__":
    asyncio.run(main())
