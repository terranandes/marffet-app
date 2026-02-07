
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.market_cache import MarketCache
from app.services.split_detector import get_split_detector
import pandas as pd

def main():
    print("Loading Market Cache...")
    prices_db = MarketCache.get_prices_db()
    detector = get_split_detector()
    
    unique_ids = set()
    for year_data in prices_db.values():
        unique_ids.update(year_data.keys())
        
    print(f"Scanning {len(unique_ids)} stocks for splits...")
    
    split_counts = 0
    stocks_with_splits = []
    
    for i, stock_id in enumerate(sorted(unique_ids)):
        history = MarketCache.get_stock_history_fast(stock_id)
        if not history:
            continue
            
        splits = detector.detect_splits(stock_id, history)
        if splits:
            split_counts += len(splits)
            stocks_with_splits.append({
                "id": stock_id,
                "count": len(splits),
                "years": [s.year for s in splits]
            })
            
    print("\n" + "="*50)
    print("SPLIT DETECTION REPORT")
    print("="*50)
    print(f"Total Stocks Scanned: {len(unique_ids)}")
    print(f"Stocks with Splits:   {len(stocks_with_splits)} ({len(stocks_with_splits)/len(unique_ids)*100:.1f}%)")
    print(f"Total Split Events:   {split_counts}")
    print("\nSample Split Stocks:")
    for s in stocks_with_splits[:10]:
        print(f"  {s['id']}: {s['count']} splits {s['years']}")
        
    if "0050" in [s['id'] for s in stocks_with_splits]:
        print("\n✅ 0050 Split Detected (Confirmed)")
    else:
        print("\n❌ 0050 Split NOT Detected (Unexpected)")

if __name__ == "__main__":
    main()
