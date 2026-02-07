import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.project_tw.strategies.mars import MarsStrategy

async def main():
    print("--- Debugging TSMC (2330) ROI ---")
    print(f"CWD: {os.getcwd()}")
    strategy = MarsStrategy()
    print(f"Crawler Data Dir: {strategy.crawler.data_dir}")
    
    # 1. Fetch Prices explicitly to check cache
    print("Checking Market Prices via Strategy...")
    # We simulate what analyze_stock_batch does but with logging
    
    years = list(range(2010, 2026 + 1))
    
    # Check Crawler Cache for 2330
    print(f"Checking Cache for 2330 in {strategy.crawler.data_dir}...")
    
    found_start = False
    found_end = False
    
    start_price = 0.0
    end_price = 0.0
    
    # Load 2010
    path_2010 = os.path.join(strategy.crawler.data_dir, "Market_2010_Prices.json")
    if os.path.exists(path_2010):
        import json
        with open(path_2010) as f:
            data = json.load(f)
            if '2330' in data:
                print(f"2010 Data for 2330: {data['2330']}")
                start_price = data['2330'].get('start', 0)
                found_start = True
            else:
                print("2330 NOT found in 2010 Cache!")
    else:
        print("2010 Cache NOT found!")

    # Load 2026
    path_2026 = os.path.join(strategy.crawler.data_dir, "Market_2026_Prices.json")
    if os.path.exists(path_2026):
        import json
        with open(path_2026) as f:
            data = json.load(f)
            if '2330' in data:
                print(f"2026 Data for 2330: {data['2330']}")
                end_price = data['2330'].get('end', 0)
                # If end is 0 (maybe early in year?), try start
                if end_price == 0:
                     end_price = data['2330'].get('start', 0)
                found_end = True
            else:
                print("2330 NOT found in 2026 Cache!")
    else:
        print("2026 Cache NOT found!")
        
    print(f"Start Price (2010): {start_price}")
    print(f"End Price (2026): {end_price}")
    
    # Run Actual Strategy Logic
    print("\nRunning Strategy.analyze_stock_batch(['2330'])...")
    results = await strategy.analyze_stock_batch(['2330'], 2010, 2026, status_callback=lambda m, p=0: print(f"cb: {m}"))
    print("\nStrategy Results:")
    for r in results:
        print(r)

if __name__ == "__main__":
    asyncio.run(main())
