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
from app.services.market_db import get_connection

async def verify_and_scan():
    # 1. Check TSMC
    print("🚀 Verifying TSMC Benchmark...")
    strategy = MarsStrategy()
    res = await strategy.analyze(['2330'], start_year=2006, principal=1000000, contribution=60000)
    
    EXCEL_PATH = 'app/project_tw/references/stock_list_s2006e2026_filtered.xlsx'
    legacy = pd.read_excel(EXCEL_PATH)
    legacy['id_str'] = legacy['id'].astype(str)
    
    l_tsmc_row = legacy[legacy['id_str'] == '2330']
    if l_tsmc_row.empty:
        print("❌ TSMC 2330 not found in legacy Excel.")
        l_tsmc = 0
    else:
        l_tsmc = l_tsmc_row['s2006e2026bao'].values[0]
    
    new_tsmc = res[0].get('s2006e2026bao') if res else 0
    print(f"TSMC -> Legacy: {l_tsmc}%, New: {new_tsmc}% (Diff: {abs(new_tsmc-l_tsmc):.2f})")
    
    # 2. Scan Price Anomalies (Global)
    print("\n🔍 Scanning for single-day price spikes (>4x in-n-out)...")
    conn = get_connection(read_only=True)
    all_prices = conn.execute("SELECT stock_id, date, close FROM daily_prices ORDER BY stock_id, date").df()
    conn.close()
    
    anomalies = []
    
    for sid, group in all_prices.groupby('stock_id'):
        closes = group['close'].values
        dates = group['date'].values
        
        for i in range(1, len(closes) - 1):
            prev = closes[i-1]
            curr = closes[i]
            nxt = closes[i+1]
            
            if prev > 0 and nxt > 0:
                # Spike detect: Up > 4x and Down > 4x back near prev
                if curr > prev * 4.0 and curr > nxt * 4.0:
                    anomalies.append({
                        'stock_id': sid,
                        'date': str(dates[i]),
                        'price': curr,
                        'prev': prev,
                        'next': nxt
                    })
                # Dip detect: Down < 0.25x and Up > 4x back
                elif curr < prev * 0.25 and curr < nxt * 0.25:
                    anomalies.append({
                        'stock_id': sid,
                        'date': str(dates[i]),
                        'price': curr,
                        'prev': prev,
                        'next': nxt
                    })

    print(f"Found {len(anomalies)} price anomalies.")
    if anomalies:
        for a in anomalies[:10]:
            print(f" - {a['stock_id']} on {a['date']}: {a['price']} (Prev: {a['prev']}, Next: {a['next']})")
            
    with open('tests/performance/price_anomalies.json', 'w') as f:
        json.dump(anomalies, f, indent=2)

if __name__ == "__main__":
    asyncio.run(verify_and_scan())
