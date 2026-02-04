
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:8000"

def measure_endpoint(name, url):
    t0 = time.time()
    try:
        resp = requests.get(url)
        dur = time.time() - t0
        status = resp.status_code
        size = len(resp.content)
        print(f"[{name}] Status: {status} | Time: {dur:.4f}s | Size: {size} bytes")
        return dur
    except Exception as e:
        print(f"[{name}] Failed: {e}")
        return 999

def verify_singleton():
    print("--- Verifying MarketCache Singleton Reuse ---")
    
    # 1. Mars Strategy (Heavy Calc)
    print("\n1. Mars Strategy (/api/results)")
    t1 = measure_endpoint("Mars", f"{BASE_URL}/api/results?start_year=2006")
    
    # 2. BCR (Different View, Same Data)
    print("\n2. Bar Chart Race (/api/race-data)")
    t2 = measure_endpoint("BCR", f"{BASE_URL}/api/race-data?start_year=2006")
    
    # 3. Concurrent Hits (Simulate Tabs opening together)
    print("\n3. Concurrent Access (Mars + BCR + Admin)")
    with ThreadPoolExecutor(max_workers=3) as executor:
        f1 = executor.submit(measure_endpoint, "Mars_Concurrent", f"{BASE_URL}/api/results")
        f2 = executor.submit(measure_endpoint, "BCR_Concurrent", f"{BASE_URL}/api/race-data")
        f3 = executor.submit(measure_endpoint, "Health", f"{BASE_URL}/health")
        
        results = [f1.result(), f2.result(), f3.result()]
        
    print("\n--- Verdict ---")
    if all(t < 0.5 for t in results):
        print("PASS: All Concurrent Responses < 0.5s (RAM Hit)")
    else:
        print("FAIL: Latency detected (Disk Read?)")

if __name__ == "__main__":
    verify_singleton()
