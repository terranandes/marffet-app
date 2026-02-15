import asyncio
import os
import sys
import pandas as pd
import numpy as np

# Ensure we can import app
sys.path.append(os.getcwd())

from app.services.strategy_service import MarsStrategy
from app.services.market_db import get_connection
from pathlib import Path

async def correlate_all_v2():
    print("🚀 Starting Grand Correlation v2 (DuckDB vs Legacy Excel)...")
    
    # 1. Load Legacy Truth
    EXCEL_PATH = "app/project_tw/references/stock_list_s2006e2026_filtered.xlsx"
    if not os.path.exists(EXCEL_PATH):
        print(f"❌ Excel not found at {EXCEL_PATH}")
        return
        
    legacy_df = pd.read_excel(EXCEL_PATH)
    legacy_df['id_str'] = legacy_df['id'].astype(str).str.zfill(4).str.replace(".0", "", regex=False)
    print(f"📄 Loaded {len(legacy_df)} stocks from legacy Excel.")

    # 2. Check Data Presence in DuckDB
    conn = get_connection(read_only=True)
    stats_df = conn.execute("""
        SELECT stock_id, MIN(date) as first_date, MAX(date) as last_date, COUNT(*) as days
        FROM daily_prices
        GROUP BY stock_id
    """).df()
    stats_map = stats_df.set_index('stock_id').to_dict('index')

    # 3. Run New Engine Simulation
    strategy = MarsStrategy()
    stock_ids = legacy_df['id_str'].tolist()
    
    print(f"⚙️ Running simulation for {len(stock_ids)} stocks using DuckDB...")
    current_results = await strategy.analyze(stock_ids, start_year=2006, principal=1000000, contribution=60000)
    results_map = {str(r['stock_code']): r for r in current_results}

    # 4. Correlation Analysis
    comparison = []
    
    for _, row in legacy_df.iterrows():
        sid = row['id_str']
        legacy_cagr = row.get('s2006e2026bao', 0)
        
        db_info = stats_map.get(sid, {})
        res = results_map.get(sid, {})
        new_cagr = res.get('s2006e2026bao', 0)
        
        diff = abs(new_cagr - legacy_cagr) if new_cagr is not None else None
        
        comparison.append({
            "id": sid,
            "name": row['name'],
            "legacy": legacy_cagr,
            "new": new_cagr,
            "diff": round(diff, 2) if diff is not None else None,
            "first_date": db_info.get('first_date'),
            "years": res.get('s2006e2026yrs')
        })

    comp_df = pd.DataFrame(comparison)
    
    # 5. Report Findings
    print(f"\n📈 Correlation Summary:")
    perfect = comp_df[comp_df['diff'] < 0.1]
    close = comp_df[comp_df['diff'] < 1.0]
    print(f" - Perfect Matches (<0.1%): {len(perfect)} ({len(perfect)/len(comp_df)*100:.1f}%)")
    print(f" - High Correlation (<1.0%): {len(close)} ({len(close)/len(comp_df)*100:.1f}%)")
    
    print("\n⚠️ Data Gap Analysis:")
    gaps = comp_df[comp_df['first_date'] > pd.Timestamp('2006-01-05')]
    print(f" - Stocks with Data Gaps (Start > 2006-01-05): {len(gaps)}")
    for _, g in gaps.head(10).iterrows():
        print(f"   - {g['id']} ({g['name']}): Starts {g['first_date']}, Legacy={g['legacy']}%, New={g['new']}%")

    print("\n⚠️ Largest Discrepancies (for stocks WITH full data):")
    full_data = comp_df[comp_df['first_date'] <= pd.Timestamp('2006-01-05')]
    outliers = full_data.sort_values('diff', ascending=False)
    for _, o in outliers.head(10).iterrows():
        print(f"   - {o['id']} ({o['name']}): Legacy={o['legacy']}%, New={o['new']}%, Diff={o['diff']}%")

if __name__ == "__main__":
    asyncio.run(correlate_all_v2())
