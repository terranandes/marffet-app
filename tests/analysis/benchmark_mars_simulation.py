"""
Benchmark Mars Strategy Simulation (Full Universe 2000-2025)

Goal:
1. Load all stocks from DuckDB.
2. Run MarsStrategy.analyze() for ALL stocks in one batch (testing bulk loop).
3. Measure wall time (Target < 100s).
4. Output sample CAGRs.
"""

import time
import duckdb
import pandas as pd
import sys
import os
import asyncio

# Add project root path
sys.path.append(os.getcwd())

from app.services.strategy_service import MarsStrategy

async def run_benchmark():
    print("Initializing Mars Strategy Benchmark...")
    
    # 1. Get list of all stocks
    conn = duckdb.connect('data/market.duckdb', read_only=True)
    res = conn.execute("SELECT DISTINCT stock_id FROM daily_prices").fetchall()
    stocks = [r[0] for r in res]
    conn.close()
    
    print(f"Loaded {len(stocks)} stocks from DB.")
    
    strategy = MarsStrategy()
    
    print(f"Starting BULK analysis for {len(stocks)} stocks (2000-2025)...")
    start_time = time.time()
    
    # Execute Async
    results = await strategy.analyze(
        stock_ids=stocks,
        start_year=2000,
        principal=100_000,
        contribution=10_000
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nBenchmark Complete!")
    print(f"Total Time: {duration:.2f}s")
    print(f"Stocks Processed: {len(results)}")
    if duration > 0:
        print(f"Throughput: {len(results)/duration:.1f} stocks/sec")
    
    # Convert to DataFrame for analysis
    if not results:
        print("No results returned.")
        return

    df = pd.DataFrame(results)
    
    # Check key columns exist
    # calculate_complex_simulation returns: cagr_pct, final_total_value, etc.
    # The analyze wrapper adds: stock_code, cagr_stats
    
    print("\n=== Sample CAGRs (TSMC, 0050, Hon Hai) ===")
    samples = ['2330', '0050', '2317']
    # Use 'cagr_pct' or check keys
    cols = ['stock_code', 'cagr_pct', 'valid_lasting_years']
    print(df[df['stock_code'].isin(samples)][cols].to_string(index=False))
    
    print("\n=== Top 5 Performers ===")
    print(df.sort_values('cagr_pct', ascending=False).head(5)[cols])
    
    print("\n=== Bottom 5 Performers ===")
    print(df.sort_values('cagr_pct', ascending=True).head(5)[cols])

def main():
    asyncio.run(run_benchmark())

if __name__ == "__main__":
    main()
