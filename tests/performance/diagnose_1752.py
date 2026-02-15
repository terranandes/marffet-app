import asyncio
import os
import sys
import pandas as pd
import json

# Ensure we can import app
sys.path.append(os.getcwd())

from app.services.strategy_service import MarsStrategy
from app.services.market_data_provider import MarketDataProvider
from app.services.roi_calculator import ROICalculator

async def diagnose_1752():
    print("🔍 Diagnosing 1752 (南光)...")
    
    code = '1752'
    start_year = 2006
    
    # 1. Inspect Data in provider
    prices = MarketDataProvider.get_daily_history_df(code, start_date=f"{start_year}-01-01")
    divs = MarketDataProvider.get_dividends(code, start_year=start_year)
    
    print(f"Prices: {len(prices)} rows")
    if not prices.empty:
        print(f"First Price ({prices['date'].iloc[0]}): {prices['close'].iloc[0]}")
        print(f"Last Price ({prices['date'].iloc[-1]}): {prices['close'].iloc[-1]}")
    
    print(f"Dividends: {json.dumps(divs, indent=2)}")
    
    # 2. Run Strategy step by step
    strategy = MarsStrategy()
    
    # We will patch the calculator inside strategy to print during simulation
    original_calc = strategy.calculator.calculate_complex_simulation
    def patched_calc(*args, **kwargs):
        # We can't easily patch a method to print inside its loop without re-implementing 
        # or using a breakpoint. Let's just run it and look at the returns.
        return original_calc(*args, **kwargs)
    
    strategy.calculator.calculate_complex_simulation = patched_calc
    
    results = await strategy.analyze([code], start_year=start_year)
    
    if results:
        res = results[0]
        print(f"\nFinal Result for 1752:")
        print(f" - CAGR: {res.get('cagr_pct')}%")
        print(f" - Final Value: {res.get('finalValue')}")
        print(f" - Total Cost: {res.get('totalCost')}")
        
        # Look at history
        history = res.get('history', [])
        print("\nYearly History Trace:")
        for h in history:
            print(f" Year {h['year']}: Value={h['value']}, Invested={h['invested']}, ROI={h['roi']}%")
    else:
        print("❌ No results returned for 1752")

if __name__ == "__main__":
    asyncio.run(diagnose_1752())
