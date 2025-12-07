import asyncio
import os
import pandas as pd
from project_tw.strategies.mars import MarsStrategy

async def main():
    print("Starting Mars Analysis Batch...")
    
    # 1. Define Stock Universe
    # In a real scenario, read from references/stock_list...xlsx
    # For now, we use a sample list + the user's demo request
    # If references/stock_list.xlsx exists, we could use it.
    
    stock_universe = ['2330', '2317', '2454', '2412', '0050', '2303', '2881', '2882']
    # TODO: Load full list from references if needed
    
    start_year = 2006
    end_year = 2025 # As per user filename request
    
    strategy = MarsStrategy()
    
    print(f"Analyzing {len(stock_universe)} stocks from {start_year} to {end_year}...")
    results = await strategy.analyze_stock_batch(stock_universe, start_year, end_year)
    
    print(f"Analysis complete. Metrics calculated for {len(results)} stocks.")
    
    # Filter and Rank
    top_50 = strategy.filter_and_rank(results, std_threshold=20.0)
    print(f"Selected {len(top_50)} qualified stocks (Low Volatility).")
    
    # Export
    output_dir = "project_tw/output"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"stock_list_s{start_year}e{end_year}_filtered.xlsx"
    output_path = os.path.join(output_dir, filename)
    
    strategy.save_to_excel(output_path)

if __name__ == "__main__":
    asyncio.run(main())
