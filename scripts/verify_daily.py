from app.services.market_cache import MarketCache
import logging

logging.basicConfig(level=logging.INFO)

def verify_daily():
    print("--- Verifying Daily Data Availability ---")
    db = MarketCache.get_prices_db(force_reload=True) 
    # Force reload to pick up new JSONs
    
    # 2330 should have daily data
    hist = MarketCache.get_stock_history_fast("2330")
    
    # Check 2006
    cnt_2006 = sum(1 for h in hist if h['year'] == 2006)
    print(f"2330 (2006) Records: {cnt_2006}")
    
    if cnt_2006 > 200:
        print("PASS: High Resolution Data Found (>200 days).")
        first = hist[0]
        print(f"Sample: {first}")
        if 'date' in first:
            print("PASS: 'date' field exists.")
        else:
            print("FAIL: 'date' field missing.")
    else:
        print(f"FAIL: Only {cnt_2006} records found (Likely Summary Only).")

    # 1101 should NOT have daily data (was skipped in Verification Mode)
    # Actually wait, I did not delete the old file for 1101? 
    # The scraper UPDATES keys. so 1101 should still be V1 (Summary).
    
    hist_1101 = MarketCache.get_stock_history_fast("1101")
    cnt_1101 = sum(1 for h in hist_1101 if h['year'] == 2006)
    print(f"1101 (2006) Records: {cnt_1101}")
    if cnt_1101 == 1:
        print("PASS: 1101 remains Summary only (V1 backward compatibility).")
    else:
        print(f"NOTE: 1101 has {cnt_1101} records.")

if __name__ == "__main__":
    verify_daily()
