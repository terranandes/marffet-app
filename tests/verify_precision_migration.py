
import requests
import time

BASE_URL = "http://localhost:8000"

def verify_consistency(stock_id="2330"):
    print(f"--- Verifying Consistency for {stock_id} ---")
    
    # 1. Get Detail (Precision Engine)
    print("Fetching Detail (Precision)...")
    t0 = time.time()
    resp_detail = requests.get(f"{BASE_URL}/api/results/detail?stock_id={stock_id}")
    t1 = time.time()
    if resp_detail.status_code != 200:
        print(f"Failed to get detail: {resp_detail.text}")
        return
    detail_data = resp_detail.json()
    detail_val = detail_data["BAO"]["finalValue"]
    print(f"Detail Final Value: {detail_val} (Time: {t1-t0:.2f}s)")
    
    # 2. Get Race List (Now Precision Engine too)
    print("Fetching Race List (Batch Precision)...")
    t0 = time.time()
    resp_race = requests.get(f"{BASE_URL}/api/race-data")
    t1 = time.time()
    
    if resp_race.status_code != 200:
        print(f"Failed to get race data: {resp_race.text}")
        return
        
    race_data = resp_race.json()
    print(f"Race List Time: {t1-t0:.2f}s (Should support ~1700 stocks)")
    
    # Find stock in list
    matched = None
    for item in race_data:
        if str(item['id']) == str(stock_id):
            matched = item
            break
            
    if not matched:
        print(f"Stock {stock_id} not found in race data")
        return
        
    list_val = matched['wealth'] 
    
    # Get all records for this stock in flattened list
    stock_records = [r for r in race_data if str(r['id']) == str(stock_id)]
    last_record = sorted(stock_records, key=lambda x: x['year'])[-1]
    
    list_final = last_record['wealth']
    print(f"List Final Value (2026): {list_final}")
    
    diff = abs(detail_val - list_final)
    print(f"Diff: {diff}")
    
    if diff < 1.0:
        print("✅ SUCCESS: Values Match!")
    else:
        print("❌ FAILURE: Mismatch!")

if __name__ == "__main__":
    time.sleep(2) 
    verify_consistency()
