import asyncio
import os
import sys
import pandas as pd
import numpy as np
import json
from datetime import datetime

# Ensure we can import app
sys.path.append(os.getcwd())

from app.services.strategy_service import MarsStrategy
from app.services.market_data_provider import MarketDataProvider

async def run_audit():
    print("🚀 Starting Global Data Audit...")
    
    # 1. Load Legacy Data
    EXCEL_PATH = 'app/project_tw/references/stock_list_s2006e2026_filtered.xlsx'
    if not os.path.exists(EXCEL_PATH):
        print(f"❌ Legacy Excel not found at {EXCEL_PATH}")
        return
        
    legacy_df = pd.read_excel(EXCEL_PATH)
    legacy_df['id_str'] = legacy_df['id'].astype(str)
    legacy_map = legacy_df.set_index('id_str')['s2006e2026bao'].to_dict()
    
    # 2. Run Simulations for all legacy stocks
    stock_ids = list(legacy_map.keys())
    print(f"📄 Auditing {len(stock_ids)} stocks...")
    
    strategy = MarsStrategy()
    all_results = await strategy.analyze(stock_ids, start_year=2006)
    
    outliers = []
    dividend_yield_outliers = []
    
    results_map = {r['stock_code']: r for r in all_results}
    
    for sid in stock_ids:
        if sid not in results_map:
            continue
            
        res = results_map[sid]
        new_cagr = res.get('s2006e2026bao', 0)
        legacy_cagr = legacy_map.get(sid, 0)
        
        diff = abs(new_cagr - legacy_cagr)
        
        # 3. Check for CAGR Outliers
        if diff > 10.0:  # 10% absolute difference is huge for CAGR
            outliers.append({
                'stock_id': sid,
                'legacy': legacy_cagr,
                'new': new_cagr,
                'diff': round(diff, 2)
            })
            
        # 4. Check for Impossible Dividends (Yield > 30% in history)
        history = res.get('history', [])
        for h in history:
            year = h['year']
            # We need the price for that year to check yield
            # Let's estimate from ROI jump or just check absolute cash vs portfolio value
            # Actually, let's check the raw dividends for this stock directly for better precision
            pass
            
    # Granular Dividend Yield Scan (Special check)
    print("🔍 Scanning for high dividend yield outliers (>30%)...")
    for sid in stock_ids:
        divs = MarketDataProvider.get_dividends(sid)
        # We need a price reference to calculate yield. Let's use avg price for that year.
        # This is a bit slow but necessary.
        for d in divs:
            year = d['year']
            cash = d['cash']
            if cash > 20.0: # Absolute high dividend is rare in TW (except some high-priced stocks)
                dividend_yield_outliers.append({
                    'stock_id': sid,
                    'year': year,
                    'cash': cash,
                    'reason': 'Absolute cash > 20'
                })
            elif cash > 10.0:
                # Check price
                p = MarketDataProvider.get_daily_history(sid, start_date=f"{year}-01-01", end_date=f"{year}-12-31")
                if p:
                    avg_p = sum(r['c'] for r in p) / len(p)
                    yield_pct = (cash / avg_p) * 100
                    if yield_pct > 30.0:
                        dividend_yield_outliers.append({
                            'stock_id': sid,
                            'year': year,
                            'cash': cash,
                            'avg_price': round(avg_p, 2),
                            'yield': round(yield_pct, 1),
                            'reason': 'Yield > 30%'
                        })

    # 5. Save Results
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_stocks': len(stock_ids),
        'cagr_outliers_count': len(outliers),
        'dividend_outliers_count': len(dividend_yield_outliers),
        'cagr_outliers': sorted(outliers, key=lambda x: x['diff'], reverse=True)[:50],
        'dividend_outliers': dividend_yield_outliers
    }
    
    with open('tests/performance/audit_report.json', 'w') as f:
        json.dump(report, f, indent=2)
        
    print(f"\n✅ Audit Complete!")
    print(f" - CAGR Outliers (>10% diff): {len(outliers)}")
    print(f" - Dividend Outliers (>30% yield): {len(dividend_yield_outliers)}")
    print(f"📝 Report saved to tests/performance/audit_report.json")

if __name__ == "__main__":
    asyncio.run(run_audit())
