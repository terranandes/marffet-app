import asyncio
import pandas as pd
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.project_tw.strategies.mars import MarsStrategy

# Paths
base_dir = os.getcwd()
csv_path = os.path.join(base_dir, "app/project_tw/stock_list.csv")
file_filtered = os.path.join(base_dir, "app/project_tw/references/stock_list_s2010e2026_filtered.xlsx")
report_path = os.path.join(base_dir, "tests/evidence/roi_universe_correlation.csv")

def clean_id(val):
    try:
        s = str(int(float(val)))
        return s.zfill(4)
    except:
        return str(val).strip()

async def main():
    print("--- ROI Universe Verification (Unfiltered Input -> Engine -> Filtered Output) ---")
    
    # 1. Load Unfiltered Universe from ISIN Source (stock_list.csv)
    print(f"Loading Unfiltered Universe from {csv_path}...")
    if not os.path.exists(csv_path):
        print("Error: stock_list.csv not found.")
        return

    df_source = pd.read_csv(csv_path)
    # Filter for Common Stocks (Listed + OTC)
    # Note: 'Bond' is excluded.
    df_universe = df_source[df_source['market_type'].isin(['Listed', 'OTC'])].copy()
    
    df_universe['clean_id'] = df_universe['code'].apply(clean_id)
    all_target_ids = df_universe['clean_id'].tolist()
    
    print(f"Source Universe (Listed+OTC): {len(all_target_ids)} stocks.")
    
    # 2. Load Golden Answer (for comparison only)
    print(f"Loading Golden Answer from {file_filtered}...")
    df_gold = pd.read_excel(file_filtered)
    df_gold['clean_id'] = df_gold['id'].apply(lambda x: str(int(float(x))).zfill(4) if pd.notna(x) and isinstance(x, (int, float)) else str(x).strip())
    
    roi_col = 's2010e2026bao'
    gold_map = {}
    for _, row in df_gold.iterrows():
        sid = row['clean_id']
        val = row[roi_col]
        gold_map[sid] = val
        
    print(f"Golden Universe: {len(gold_map)} stocks.")

    # 3. Run Engine (Apply Our Filtering)
    print("Initializing MarsStrategy...")
    strategy = MarsStrategy()
    
    start_year = 2010
    end_year = 2026
    
    print(f"Running Analysis for {len(all_target_ids)} stocks ({start_year}-{end_year})...")
    
    def progress(msg, pct=0):
        print(f"[Engine] {msg} ({pct}%)")

    # This runs the engine logic. 
    # The engine naturally 'filters' by returning results only for valid stocks.
    results = await strategy.analyze_stock_batch(all_target_ids, start_year, end_year, status_callback=progress)
    
    print(f"Engine Analysis Complete. Valid Stocks (Our Filtered List): {len(results)}")

    # 4. Compare
    comparison = []
    
    # Track intersection
    engine_ids = set()
    
    for res in results:
        sid = res.get('stock_code')
        engine_ids.add(sid)
        engine_cagr = res.get('cagr_pct', 0.0)
        
        # Look up in golden map
        gold_cagr = gold_map.get(sid, None) # None if not in gold
        
        if gold_cagr is not None:
            diff = engine_cagr - gold_cagr
            abs_diff = abs(diff)
            status = "MATCH" if abs_diff < 1.0 else "MISMATCH"
        else:
            diff = 0.0
            abs_diff = 0.0
            status = "ENGINE_ONLY" # We have it, they don't
            gold_cagr = 0.0 # Placeholder
            
        comparison.append({
            'code': sid,
            'name': res.get('stock_name', ''),
            'engine_cagr': round(engine_cagr, 2),
            'gold_cagr': round(gold_cagr, 2),
            'diff': round(diff, 2),
            'abs_diff': round(abs_diff, 2),
            'status': status,
            'valid_years': res.get('valid_lasting_years', 0)
        })
        
    # Also check for stocks in Gold but NOT in Engine (GOLD_ONLY)
    for gid in gold_map:
        if gid not in engine_ids:
            comparison.append({
                'code': gid,
                'name': 'Unknown',
                'engine_cagr': 0.0,
                'gold_cagr': round(gold_map[gid], 2),
                'diff': 0.0,
                'abs_diff': 0.0,
                'status': 'GOLD_ONLY',
                'valid_years': 0
            })
            
    df_comp = pd.DataFrame(comparison)
    
    # Sort
    df_comp.sort_values(by=['status', 'abs_diff'], ascending=[True, False], inplace=True)
    
    # Save
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    df_comp.to_csv(report_path, index=False)
    print(f"\nReport saved to: {report_path}")
    
    # Summary Props
    total_engine = len(engine_ids)
    total_gold = len(gold_map)
    intersection = df_comp[df_comp['status'].isin(['MATCH', 'MISMATCH'])]
    matches = df_comp[df_comp['status'] == 'MATCH']
    
    print(f"\n--- ROI Universe Verification Summary ---")
    print(f"Source Universe (Listed+OTC): {len(all_target_ids)}")
    print(f"Our Filtered List (Engine Valid): {total_engine}")
    print(f"MoneyCome Filtered List (Golden): {total_gold}")
    print(f"Intersection: {len(intersection)}")
    print(f"CAGR Matches (<1% diff) in Intersection: {len(matches)} ({len(matches)/len(intersection)*100:.1f}%)")
    
    print("\n[Top 10 Discrepancies (MISMATCH)]")
    print(df_comp[df_comp['status'] == 'MISMATCH'].head(10).to_string(index=False))

    print("\n[Top 10 Matches]")
    print(matches.head(10).to_string(index=False))
    
    print("\n[Sample GOLD_ONLY (Missed by Engine)]")
    print(df_comp[df_comp['status'] == 'GOLD_ONLY'].head(5).to_string(index=False))

    print("\n[Sample ENGINE_ONLY (Extra in Engine)]")
    print(df_comp[df_comp['status'] == 'ENGINE_ONLY'].head(5).to_string(index=False))

if __name__ == "__main__":
    asyncio.run(main())
