import json
import asyncio
from app.services.market_data_provider import MarketDataProvider
from app.services.split_detector import get_split_detector

async def scan_splits():
    sd = get_split_detector()
    
    # Efficiently get stocks that actually have prices
    from app.services.market_db import get_connection
    conn = get_connection(read_only=True)
    stocks = [r[0] for r in conn.execute("SELECT DISTINCT stock_id FROM daily_prices").fetchall()]
    conn.close()
    
    all_splits = {}
    
    print(f"Scanning splits for {len(stocks)} stocks...")
    
    for i, s in enumerate(stocks):
        h = MarketDataProvider.get_daily_history(s)
        if not h:
            continue
            
        splits = sd.detect_splits(s, h)
        if splits:
            all_splits[s] = [{'year': sp.year, 'ratio': sp.ratio} for sp in splits]
            
        if (i + 1) % 500 == 0:
            print(f"  Scanned {i+1}/{len(stocks)}...")
            
    with open('tests/performance/all_detected_splits.json', 'w') as f:
        json.dump(all_splits, f, indent=2)
    
    print(f"Scan complete. Found splits for {len(all_splits)} stocks.")

if __name__ == "__main__":
    asyncio.run(scan_splits())
