from app.services.stock_info_service import StockInfoService
import pandas as pd
import os

def test_fetch():
    print("Testing O(1) Fetch...")
    df = StockInfoService.fetch_stock_list()
    
    if df.empty:
        print("❌ Fetch failed or returned empty.")
        exit(1)
        
    print(f"✅ Fetched {len(df)} rows.")
    print("Sample Data:")
    print(df.head())
    
    # Check for TSMC
    tsmc = df[df['code'] == '2330']
    if not tsmc.empty:
        print(f"✅ Found TSMC: {tsmc.iloc[0]['name']}")
    else:
        print("❌ TSMC not found!")

    # Check for an OTC stock (e.g. 5274 ASPEED or similar)
    # 8069 (PChome) is OTC
    pchome = df[df['code'] == '8069']
    if not pchome.empty:
        print(f"✅ Found PChome (OTC): {pchome.iloc[0]['name']}")

    # Check for CB (11011)
    cb = df[df['code'] == '11011']
    if not cb.empty:
        print(f"✅ Found CB 11011: {cb.iloc[0]['name']}")
    else:
        print("❌ CB 11011 Not Found!")

    # Check for Specific User Target 65331
    target = df[df['code'] == '65331']
    if not target.empty:
        print(f"✅ Found Target 65331: {target.iloc[0]['name']}")
    else:
        print("❌ Target 65331 Not Found!")
        
    print("\nTesting Update Cache...")
    cache_path = "app/project_tw/stock_list_test.csv"
    StockInfoService.update_cache(cache_path)
    
    if os.path.exists(cache_path):
        print(f"✅ Cache file created at {cache_path}")
        # Clean up
        os.remove(cache_path)
    else:
        print("❌ Cache file verification failed.")

if __name__ == "__main__":
    test_fetch()
