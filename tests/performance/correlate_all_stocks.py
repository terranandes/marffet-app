import asyncio
import os
import sys
import pandas as pd
import numpy as np

# Ensure we can import app
sys.path.append(os.getcwd())

from app.services.strategy_service import MarsStrategy
from pathlib import Path

async def correlate_all():
    print("🚀 Starting Grand Correlation (DuckDB vs Legacy Excel)...")
    
    # 1. Load Legacy Truth
    EXCEL_PATH = "app/project_tw/references/stock_list_s2006e2026_filtered.xlsx"
    if not os.path.exists(EXCEL_PATH):
        print(f"❌ Excel not found at {EXCEL_PATH}")
        return
        
    legacy_df = pd.read_excel(EXCEL_PATH)
    legacy_df['id_str'] = legacy_df['id'].astype(str)
    print(f"📄 Loaded {len(legacy_df)} stocks from legacy Excel.")

    # 2. Run New Engine Simulation for the same IDs
    strategy = MarsStrategy()
    stock_ids = legacy_df['id_str'].tolist()
    
    print(f"⚙️ Running simulation for {len(stock_ids)} stocks using DuckDB...")
    # 2006 to 2026, 1M principal, 60k contribution
    current_results = await strategy.analyze(stock_ids, start_year=2006, principal=1000000, contribution=60000)
    print(f"✅ Simulation complete. Received {len(current_results)} results.")

    # 3. Correlation Analysis
    comparison = []
    matches = 0
    close_matches = 0 # within 1% absolute diff
    
    results_map = {str(r['stock_code']): r for r in current_results}
    
    for _, row in legacy_df.iterrows():
        sid = row['id_str']
        legacy_cagr = row.get('s2006e2026bao', 0)
        
        if sid in results_map:
            res = results_map[sid]
            new_cagr = res.get('s2006e2026bao', 0)
            
            diff = abs(new_cagr - legacy_cagr)
            comparison.append({
                "id": sid,
                "name": row['name'],
                "legacy": legacy_cagr,
                "new": new_cagr,
                "diff": round(diff, 2)
            })
            
            if diff < 0.1: matches += 1
            if diff < 1.0: close_matches += 1
        else:
            comparison.append({
                "id": sid,
                "name": row['name'],
                "legacy": legacy_cagr,
                "new": None,
                "diff": None
            })

    # 4. Summary Report
    print(f"\n📈 Correlation Summary:")
    print(f" - Total Stocks Examined: {len(legacy_df)}")
    print(f" - Results Obtained: {len(current_results)}")
    print(f" - Perfect Matches (<0.1% diff): {matches} ({matches/len(legacy_df)*100:.1f}%)")
    print(f" - High Correlation (<1.0% diff): {close_matches} ({close_matches/len(legacy_df)*100:.1f}%)")
    
    # Sort by diff to find outliers
    outliers = sorted([c for c in comparison if c['diff'] is not None], key=lambda x: x['diff'], reverse=True)
    print("\n⚠️ Largest Outliers:")
    for o in outliers[:10]:
        print(f" - {o['id']} ({o['name']}): Legacy={o['legacy']}%, New={o['new']}%, Diff={o['diff']}%")

if __name__ == "__main__":
    asyncio.run(correlate_all())
