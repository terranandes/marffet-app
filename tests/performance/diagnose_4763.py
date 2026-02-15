import asyncio
import os
import sys
import pandas as pd
import json

# Ensure we can import app
sys.path.append(os.getcwd())

from app.services.strategy_service import MarsStrategy
from app.services.market_data_provider import MarketDataProvider

async def diagnose_4763():
    print("🔍 Diagnosing 4763 (材料*-KY)...")
    
    code = '4763'
    start_year = 2006
    
    # 1. Inspect Data
    prices = MarketDataProvider.get_daily_history_df(code, start_date=f"{start_year}-01-01")
    divs = MarketDataProvider.get_dividends(code, start_year=start_year)
    
    print(f"Prices: {len(prices)} rows")
    if not prices.empty:
        print(f"First Price ({prices['date'].iloc[0]}): {prices['close'].iloc[0]}")
        print(f"Last Price ({prices['date'].iloc[-1]}): {prices['close'].iloc[-1]}")
    
    # 2. Run Strategy (Force Zero Dividends to test Adjusted Price hypothesis)
    strategy = MarsStrategy()
    
    # We can't easily pass 'ignore_dividends' to analyze yet, 
    # but we can patch MarketDataProvider.get_dividends temporarily or just overwrite divs result here.
    # Actually, analyze() fetches internally. Let's patch MarketDataProvider.
    import unittest.mock as mock
    with mock.patch('app.services.market_data_provider.MarketDataProvider.get_dividends', return_value=[]):
        results = await strategy.analyze([code], start_year=start_year)
    
    if results:
        res = results[0]
        print(f"\nFinal Result for 4763:")
        print(f" - CAGR: {res.get('cagr_pct')}%")
        print(f" - Final Value: {res.get('finalValue')}")
        
        # Look at history
        history = res.get('history', [])
        print("\nYearly History Trace:")
        for h in history:
            print(f" Year {h['year']}: Value={h['value']}, ROI={h['roi']}%")
    else:
        print("❌ No results returned for 4763")

if __name__ == "__main__":
    asyncio.run(diagnose_4763())
