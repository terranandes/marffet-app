
import logging
import asyncio
import sys
import pandas as pd
from app.services.strategy_service import MarsStrategy, CBStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_mars_strategy():
    print("=== Testing MarsStrategy ===")
    strategy = MarsStrategy()
    
    # Test 1: Single Stock (TSMC)
    stock_ids = ['2330']
    print(f"Analyzing {stock_ids}...")
    results = strategy.analyze(stock_ids, start_year=2006)
    
    if results:
        res = results[0]
        print(f"Success! {res['stock_code']} CAGR: {res.get('cagr_pct')}%")
        print(f"Years Valid: {res.get('valid_lasting_years')}")
        print(f"StdDev: {res.get('cagr_std')}")
    else:
        print("No results returned for 2330.")

    # Test 2: ETF (0050)
    stock_ids = ['0050']
    print(f"Analyzing {stock_ids}...")
    results = strategy.analyze(stock_ids, start_year=2006)
    if results:
        res = results[0]
        print(f"Success! {res['stock_code']} CAGR: {res.get('cagr_pct')}%")
    else:
        print("No results returned for 0050.")

async def test_cb_strategy():
    print("\n=== Testing CBStrategy ===")
    strategy = CBStrategy()
    
    # We need a stock that might have CBs. 
    # Usually hard to guess which one is active.
    # But let's just run it for a known one or random one.
    # 6533 Andes has had CBs (65331 etc) 
    # But checking if we have issuance data for it.
    
    # Let's just initialize and check if no errors.
    try:
        await strategy.initialize()
        print(f"CB Issuance Data Loaded: {len(strategy.issuance_data)} records")
        
        # Taking a sample issuer from issuance data to test
        if strategy.issuance_data:
            sample = strategy.issuance_data[0]
            issuer_code = sample.get('IssuerCode')
            if issuer_code:
                print(f"Testing Analysis for Issuer: {issuer_code}")
                # Analyze might be slow due to live fetch
                # results = await strategy.analyze([issuer_code])
                # print(f"Results: {len(results)}")
    except Exception as e:
        print(f"CB Strategy Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mars_strategy())
    asyncio.run(test_cb_strategy())
