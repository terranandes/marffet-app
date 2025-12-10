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
    
    # Load Full List
    stock_list_path = "project_tw/stock_list.csv"
    if os.path.exists(stock_list_path):
        df_list = pd.read_csv(stock_list_path)
        # Ensure 'code' is string
        df_list['code'] = df_list['code'].astype(str)
        # Handle 'name'
        name_map = dict(zip(df_list['code'], df_list['name']))
        stock_universe = df_list['code'].tolist()
        # stock_universe = stock_universe[:50] # Debug Limit
        # stock_universe = stock_universe[:50] # Debug Limit
        # USER REQUEST: Full Scan (incl ETFs like 0050)
        # We override to ["ALL"] to let MarsStrategy auto-detect from Market Data
        pass

    # Force ALL mode
    stock_universe = ["ALL"]
    name_map = {} # Names will be missing initially, but we can try to fill them from cache?
    # Actually, we can load names from stock_list if available, but for new ones we rely on what?
    # The current code tries to map from name_map. If missing, name remains code.
    # That is acceptable for now.
    
    if os.path.exists(stock_list_path):
         df_list = pd.read_csv(stock_list_path)
         df_list['code'] = df_list['code'].astype(str)
         name_map = dict(zip(df_list['code'], df_list['name']))
         
    # else:
    #     pass
    
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
    filename = f"stock_list_s{start_year}e{end_year}_unfiltered.xlsx"
    output_path = os.path.join(output_dir, filename)
    
    # Enrich Names
    for r in results:
        code = r.get('stock_code')
        if code and code in name_map:
            r['stock_name'] = name_map[code]
            
    # Filter and Rank (if needed, or keep all for "Scan All")
    # User said "Scan All", so we might want to skip filtering logic and just Save All
    # But MarsStrategy.filter_and_rank stores top_50.
    # Let's Modify save_to_excel to align with "results".
    # Or just assign strategy.top_50 = results (All)
    strategy.top_50 = results
    
    strategy.save_to_excel(output_path)

if __name__ == "__main__":
    asyncio.run(main())
