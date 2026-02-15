import requests
import time
import json

def test_mars_performance():
    url = "http://127.0.0.1:8000/api/results"
    params = {
        "start_year": 2010,
        "principal": 1000000,
        "contribution": 60000
    }
    
    print(f"🚀 Starting Mars Strategy Performance Test...")
    print(f"📡 Target: {url}")
    print(f"📊 Parameters: {params}")
    
    start_time = time.time()
    try:
        response = requests.get(url, params=params, timeout=300)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            count = len(data)
            print(f"✅ Success! Received {count} stock results.")
            print(f"⏱️  Total Loading Time: {elapsed:.2f} seconds")
            
            # Show a few results for verification
            if count > 0:
                print("\nSample Results (First 3):")
                for i in range(min(3, count)):
                    stock = data[i]
                    print(f" - {stock.get('id')} ({stock.get('name')}): CAGR {stock.get('cagr_pct')}%")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_mars_performance()
