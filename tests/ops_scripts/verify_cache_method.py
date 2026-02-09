from app.services.market_data_service import get_cached_prices_batch, ensure_price_cache_batch
import pandas as pd

def test_cache():
    print("Testing ensure_price_cache_batch...")
    # 2330 is TSMC
    mapping = ensure_price_cache_batch(['2330'], start_date="2024-01-01")
    print(f"Mapping: {mapping}")
    
    print("Testing get_cached_prices_batch...")
    data = get_cached_prices_batch(list(mapping.values()), start_date="2024-01-01")
    
    if '2330.TW' in data:
        s = data['2330.TW']
        print(f"Got Series with {len(s)} rows.")
        print(s.head())
        print("✅ get_cached_prices_batch works!")
    else:
        print("❌ Data not found in cache!")
        print(f"Keys: {data.keys()}")

    print("\nTesting fetch_stock_info...")
    info = market_data_service.fetch_stock_info("2330")
    print(f"Info keys: {info.keys()}")
    if info.get('lastPrice'):
        print(f"✅ fetch_stock_info works! Price: {info['lastPrice']}")
    else:
        print("❌ fetch_stock_info failed (no price)")

    print("\nTesting fetch_history_series...")
    hist = market_data_service.fetch_history_series("2330", period="5d")
    if not hist.empty:
        print(f"✅ fetch_history_series works! Rows: {len(hist)}")
    else:
        print("❌ fetch_history_series failed (empty)")

if __name__ == "__main__":
    from app.services import market_data_service
    test_cache()
