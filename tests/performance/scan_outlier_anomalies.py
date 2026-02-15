import asyncio
import os
import sys
import pandas as pd
import json

# Ensure we can import app
sys.path.append(os.getcwd())

from app.services.market_data_provider import MarketDataProvider
from app.services.split_detector import get_split_detector

async def scan_outliers():
    with open('tests/performance/audit_report.json', 'r') as f:
        report = json.load(f)
    
    outliers = report.get('cagr_outliers', [])
    print(f"🔍 Scanning {len(outliers)} CAGR outliers for price/split anomalies...")
    
    sd = get_split_detector()
    findings = []
    
    for o in outliers:
        sid = o['stock_id']
        history = MarketDataProvider.get_daily_history(sid)
        
        if not history:
            continue
            
        # 1. Scan for Price Dips (e.g. drop > 80% then back up same day or next)
        for i in range(1, len(history)-1):
            curr = history[i]['c']
            prev = history[i-1]['c']
            nxt = history[i+1]['c']
            
            if prev > 1 and curr < prev * 0.2 and nxt > curr * 4:
                findings.append({
                    'stock_id': sid,
                    'date': history[i]['date'],
                    'prev': prev,
                    'curr': curr,
                    'next': nxt,
                    'reason': '1-day Price Dip (<20% of prior/next)'
                })
        
        # 2. Check for Split Detection
        splits = sd.detect_splits(sid, history)
        if any(s.ratio > 5 for s in splits):
            findings.append({
                'stock_id': sid,
                'splits': [f"{s.date}: {s.ratio}:1" for s in splits if s.ratio > 5],
                'reason': 'Extreme Split Ratio (>5)'
            })

    print(f"\n✅ Scan Complete! Found {len(findings)} technical abnormalities.")
    for f in findings:
        print(f" - {f['stock_id']} ({f.get('date', 'split')}): {f['reason']}")
        if 'prev' in f: print(f"    p={f['prev']}, c={f['curr']}, n={f['next']}")
        if 'splits' in f: print(f"    {f['splits']}")

if __name__ == "__main__":
    asyncio.run(scan_outliers())
