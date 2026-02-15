import json
import os
import sys
import pandas as pd
from pathlib import Path

# Ensure we can import app
sys.path.append(os.getcwd())
from app.services.market_db import get_connection

def audit_basis():
    print("🔍 Auditing DuckDB Price Basis against Nominal MI_INDEX Anchors...")
    
    # 1. Load Nominal Anchors
    with open('data/yearly_nominal_prices.json', 'r') as f:
        nominal_years = json.load(f)
    
    # 2. Fetch DuckDB Checkpoints (Jan first trading day of each year)
    conn = get_connection(read_only=True)
    
    comparison = []
    
    for year_str, nominal_map in nominal_years.items():
        year = int(year_str)
        print(f"  Checking Year {year}...")
        
        # Get DuckDB prices for January of this year
        query = """
            SELECT stock_id, MIN(date) as first_date, close 
            FROM daily_prices 
            WHERE date >= ? AND date <= ?
            GROUP BY stock_id, date, close
            ORDER BY stock_id, date
        """
        # We need the FIRST trading day's close in DuckDB for that year
        # Actually a simpler way:
        df_db = conn.execute(f"SELECT stock_id, date, close FROM daily_prices WHERE year(date) = {year} ORDER BY stock_id, date").df()
        if df_db.empty: continue
        
        # Get first row per stock
        df_first = df_db.groupby('stock_id').first().reset_index()
        db_map = df_first.set_index('stock_id')['close'].to_dict()
        
        for sid, nominal_p in nominal_map.items():
            db_p = db_map.get(sid)
            if db_p is not None:
                diff_pct = abs(db_p - nominal_p) / nominal_p if nominal_p > 0 else 0
                comparison.append({
                    "stock_id": sid,
                    "year": year,
                    "nominal": nominal_p,
                    "duckdb": db_p,
                    "diff_pct": diff_pct
                })
    
    conn.close()
    
    if not comparison:
        print("❌ No overlapping data found for audit.")
        return
        
    df = pd.DataFrame(comparison)
    
    # Categorize
    # TRI: Consistent mismatch across years (usually DuckDB < Nominal because of backward adjustment)
    # Note: Backward adjustment makes PAST prices SMALLER. 
    # Current DuckDB 2330 in 2006 is ~19.5? Wait.
    # If TRI, 2006 DuckDB Price < 2006 Nominal Price.
    
    summary = df.groupby('stock_id')['diff_pct'].mean().reset_index()
    
    contaminated = summary[summary['diff_pct'] > 0.05]
    pure = summary[summary['diff_pct'] <= 0.05]
    
    print(f"\n📊 Audit Results:")
    print(f" - total Stocks Audited: {len(summary)}")
    print(f" - Pure Nominal Stocks: {len(pure)} ({len(pure)/len(summary)*100:.1f}%)")
    print(f" - Basis Mismatch (TRI?): {len(contaminated)} ({len(contaminated)/len(summary)*100:.1f}%)")
    
    # Save Report
    report = {
        "pure_stocks": pure['stock_id'].tolist(),
        "contaminated_stocks": contaminated['stock_id'].tolist(),
        "details": comparison
    }
    with open('data/basis_audit_report.json', 'w') as f:
        json.dump(report, f)
    
    print("\n⚠️ Samples of Contaminated Stocks:")
    for _, row in contaminated.head(10).merge(df[df['year']==2006], on='stock_id').iterrows():
        print(f"   - {row['stock_id']}: DuckDB={row['duckdb']}, Nominal={row['nominal']} (Diff={row['diff_pct_x']*100:.1f}%)")

if __name__ == "__main__":
    audit_basis()
