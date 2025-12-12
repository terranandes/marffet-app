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
    
    # Enrich Names (Before Filtering)
    for r in results:
        code = r.get('stock_code')
        if code and code in name_map:
            r['stock_name'] = name_map[code]
            
    # 1. Save Unfiltered High-Level Data
    print("Saving Unfiltered Results...")
    strategy.top_50 = list(results) # Copy list
    output_dir = "project_tw/output"
    os.makedirs(output_dir, exist_ok=True)
    filename_unfiltered = f"stock_list_s{start_year}e{end_year}_unfiltered.xlsx"
    output_path_unfiltered = os.path.join(output_dir, filename_unfiltered)
    strategy.save_to_excel(output_path_unfiltered)

    # 2. Filter & Rank (Result-Ranking Phase)
    print("Applying Filters & Ranking...")
    # Pass name_map to allow filtering by Name (e.g. Warrants)
    top_50 = strategy.filter_and_rank(results, stock_dict=name_map)
    print(f"Selected {len(top_50)} qualified stocks (Low Volatility <= TSMC, No Warrants/DRs/Lev, >3 Yrs).")
    
    # 3. Save Filtered Data
    filename_filtered = f"stock_list_s{start_year}e{end_year}_filtered.xlsx"
    output_path_filtered = os.path.join(output_dir, filename_filtered)
    strategy.save_to_excel(output_path_filtered)

if __name__ == "__main__":
    asyncio.run(main())
