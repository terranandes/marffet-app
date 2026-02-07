#!/usr/bin/env python3
"""
Full ROI Verification using MarsStrategy Engine.
This runs ALL stocks through our engine (not simple CAGR) and compares with MoneyCome.
"""
import asyncio
import pandas as pd
import os
import sys

# Add project root to path
sys.path.insert(0, os.getcwd())

from app.project_tw.strategies.mars import MarsStrategy

# Paths
base_dir = os.getcwd()
csv_path = os.path.join(base_dir, "app/project_tw/stock_list.csv")
file_filtered = os.path.join(base_dir, "app/project_tw/references/stock_list_s2010e2026_filtered.xlsx")
report_path = os.path.join(base_dir, "tests/evidence/roi_engine_correlation.csv")

def clean_id(val):
    try:
        s = str(int(float(val)))
        return s.zfill(4)
    except:
        return str(val).strip()

async def main():
    print("=" * 60)
    print("ROI Engine Verification (MarsStrategy)")
    print("=" * 60)
    
    # 1. Load Universe
    print(f"\n[1/4] Loading Universe from {csv_path}...")
    df_source = pd.read_csv(csv_path)
    df_universe = df_source[df_source['market_type'].isin(['Listed', 'OTC'])].copy()
    df_universe['clean_id'] = df_universe['code'].apply(clean_id)
    all_target_ids = df_universe['clean_id'].tolist()
    print(f"  → {len(all_target_ids)} stocks (Listed + OTC)")
    
    # 2. Load Golden Answer
    print(f"\n[2/4] Loading Golden Answer from Excel...")
    df_gold = pd.read_excel(file_filtered)
    df_gold['clean_id'] = df_gold['id'].apply(lambda x: str(int(float(x))).zfill(4) if pd.notna(x) and isinstance(x, (int, float)) else str(x).strip())
    
    roi_col = 's2010e2026bao'
    gold_map = {row['clean_id']: row[roi_col] for _, row in df_gold.iterrows()}
    print(f"  → {len(gold_map)} stocks in Golden Answer")

    # 3. Run Engine
    print(f"\n[3/4] Running MarsStrategy Engine (2010-2026)...")
    strategy = MarsStrategy()
    
    def progress(msg, pct=0):
        print(f"  [{pct:3d}%] {msg}")

    results = await strategy.analyze_stock_batch(all_target_ids, 2010, 2026, status_callback=progress)
    print(f"  → Engine returned {len(results)} valid stocks")

    # 4. Compare
    print(f"\n[4/4] Comparing Engine vs Golden Answer...")
    comparison = []
    engine_ids = set()
    
    for res in results:
        sid = res.get('stock_code')
        engine_ids.add(sid)
        engine_cagr = res.get('cagr_pct', 0.0)
        gold_cagr = gold_map.get(sid)
        
        if gold_cagr is not None:
            diff = engine_cagr - gold_cagr
            abs_diff = abs(diff)
            status = "MATCH" if abs_diff < 1.0 else "MISMATCH"
        else:
            diff = 0.0
            abs_diff = 0.0
            status = "ENGINE_ONLY"
            gold_cagr = 0.0
            
        comparison.append({
            'code': sid,
            'name': res.get('stock_name', ''),
            'engine_cagr': round(engine_cagr, 2),
            'gold_cagr': round(gold_cagr, 2) if gold_cagr else 0.0,
            'diff': round(diff, 2),
            'abs_diff': round(abs_diff, 2),
            'status': status,
            'valid_years': res.get('valid_lasting_years', 0)
        })
        
    # Add GOLD_ONLY
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
    df_comp.sort_values(by=['status', 'abs_diff'], ascending=[True, False], inplace=True)
    
    # Save
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    df_comp.to_csv(report_path, index=False)
    
    # Summary
    total_engine = len(engine_ids)
    total_gold = len(gold_map)
    intersection = df_comp[df_comp['status'].isin(['MATCH', 'MISMATCH'])]
    matches = df_comp[df_comp['status'] == 'MATCH']
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Engine Valid Stocks: {total_engine}")
    print(f"Golden Valid Stocks: {total_gold}")
    print(f"Intersection:        {len(intersection)}")
    print(f"MATCH (<1% diff):    {len(matches)} ({len(matches)/len(intersection)*100:.1f}%)")
    print(f"\nReport saved: {report_path}")
    
    # TSMC Example
    tsmc = df_comp[df_comp['code'] == '2330']
    if not tsmc.empty:
        print("\n--- TSMC (2330) Example ---")
        print(tsmc.to_string(index=False))
    
    # Top Discrepancies
    print("\n--- Top 10 Discrepancies ---")
    print(df_comp[df_comp['status'] == 'MISMATCH'].head(10).to_string(index=False))
    
    # Top Matches
    print("\n--- Top 10 Matches ---")
    print(matches.head(10).to_string(index=False))

if __name__ == "__main__":
    asyncio.run(main())
