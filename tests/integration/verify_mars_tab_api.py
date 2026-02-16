"""
Phase 14 Verification: Mars Strategy API Simulation

Verifies that the Mars Strategy runs correctly end-to-end using the MarsStrategy class.
This simulates the backend processing logic used by the Mars Tab.

Checks:
1. Strategy Initialization.
2. Batch Analysis (Small batch, e.g., 2330).
3. Result Structure (must contain 'cagr', 'history', etc.).
4. Data Source Verification (Implicitly checks if it runs without error).
"""

import asyncio
import sys
import os
import pandas as pd

# Add project root to path
sys.path.insert(0, os.getcwd())

from app.project_tw.strategies.mars import MarsStrategy

async def verify_mars_strategy():
    print("🚀 Initializing MarsStrategy...")
    strategy = MarsStrategy()
    
    stock_codes = ["2330"] # Test with TSMC
    start_year = 2004 # Rebuild is at 2004, so we test this
    end_year = 2025
    
    print(f"🎯 analyzing stock: {stock_codes} ({start_year}-{end_year})...")
    
    # Run analysis
    # status_callback is optional
    results = await strategy.analyze_stock_batch(
        stock_codes=stock_codes,
        start_year=start_year,
        end_year=end_year
    )
    
    print(f"\n📊 Analysis Complete. Results: {len(results)}")
    
    if not results:
        print("❌ FAIL: No results returned.")
        return
        
    res = results[0]
    print("\n🔍 Sample Result (2330):")
    print(f"   Stock: {res.get('stock_code')}")
    print(f"   CAGR: {res.get('cagr_pct', 'N/A')}%")
    print(f"   Final Price: {res.get('price', 'N/A')}")
    print(f"   Valid Years: {res.get('valid_lasting_years', 'N/A')}")
    
    # Checks
    if res.get('cagr_pct') is None:
        print("❌ FAIL: CAGR is None.")
    elif res.get('valid_lasting_years', 0) < 10:
        print("⚠️ WARNING: Valid lasting years seems low (<10). Data might be missing.")
    else:
        print("✅ PASS: Mars Strategy returned valid metrics.")

    # Filter & Rank simulation
    print("\n🔍 Testing Filter & Rank...")
    ranked = strategy.filter_and_rank(results)
    if ranked:
        print(f"✅ Filter & Rank returned {len(ranked)} items.")
    else:
        print("⚠️ Filter & Rank returned 0 items (might be filtered out?).")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_mars_strategy())
