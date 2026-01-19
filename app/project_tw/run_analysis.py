import asyncio
import os
import pandas as pd
from app.project_tw.strategies.mars import MarsStrategy

async def main(status_callback=None):
    if status_callback: status_callback("Initializing Mars Analysis Batch...")
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
        # Force Demo Mode for Speed (Top stocks + some variation)
        # Full 'ALL' scan takes hours. For development, we use a representative subset.
        # stock_universe = ["2330", "0050", "2317", "2454", "2308", "2881", "2891", "1101", "2412", "0056"]
        # Add some TPEX stocks to Verify integration (3293 IGS, 8069, 8299 Phison, 6669 Wiwynn-TWSE)
        # stock_universe.extend(["3293", "8299", "6669"])
        
        # PRODUCTION: Full Scan
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
    
    import datetime
    start_year = 2006
    end_year = datetime.datetime.now().year  # Dynamic: includes current year
    
    strategy = MarsStrategy()
    
    print(f"Analyzing {len(stock_universe)} stocks from {start_year} to {end_year}...")
    if status_callback: status_callback(f"Analyzing {len(stock_universe)} stocks ({start_year}-{end_year})...")
    
    results = await strategy.analyze_stock_batch(stock_universe, start_year, end_year, status_callback=status_callback)
    
    print(f"Analysis complete. Metrics calculated for {len(results)} stocks.")
    if status_callback: status_callback("Analysis Processing Complete. Saving results...")
    
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
