import asyncio
import os
import sys

# Ensure we can import app
sys.path.append(os.getcwd())

from app.services.strategy_service import MarsStrategy
from pathlib import Path

async def diagnose_tsmc():
    print("🔍 Diagnosing TSMC (2330) Simulation...")
    strategy = MarsStrategy()
    
    # 2006 to 2026, 1M principal, 60k contribution
    stock_ids = ["6283"]
    results = await strategy.analyze(stock_ids, start_year=2006, principal=1000000, contribution=60000)
    
    if not results:
        print("❌ No results found for TSMC (2330)")
        return
        
    res = results[0]
    print(f"\n📊 Results for {res.get('stock_code')}:")
    print(f" - Final Value: {res.get('finalValue'):,.0f}")
    print(f" - Total Cost: {res.get('totalCost'):,.0f}")
    print(f" - CAGR 2006-2026: {res.get('s2006e2026bao')}%")
    print(f" - Valid Years: {res.get('valid_lasting_years')}")
    
    print("\n📈 History (First 5 years):")
    history = res.get('history', [])
    for entry in history[:5]:
        print(f"  Year {entry['year']}: Value={entry['value']:,.0f}, ROI={entry['roi']}%")
        
    print("\n📉 History (Last 5 years):")
    for entry in history[-5:]:
        print(f"  Year {entry['year']}: Value={entry['value']:,.0f}, ROI={entry['roi']}%")

if __name__ == "__main__":
    asyncio.run(diagnose_tsmc())
