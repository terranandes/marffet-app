import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_cb_api():
    session = requests.Session()
    
    # 1. Login
    print("[Test] Logging in...")
    login_url = f"{BASE_URL}/auth/dev/login"
    res = session.get(login_url, allow_redirects=True)
    
    if res.status_code != 200:
        print(f"[Error] Login failed: {res.status_code}")
        # Note: It usually redirects to frontend (3000), but requests follows redirects. 
        # If frontend is not served by this server, it might 404.
        # But we care about the Cookie being set.
        print(f"Cookie jar: {session.cookies.get_dict()}")
    else:
        print("[Test] Login response received. Cookies:", session.cookies.get_dict())

    # 2. Fetch CB Portfolio
    print("[Test] Fetching CB Portfolio...")
    cb_url = f"{BASE_URL}/api/cb/portfolio"
    res_cb = session.get(cb_url)
    
    print(f"[Test] Status Code: {res_cb.status_code}")
    if res_cb.status_code == 200:
        data = res_cb.json()
        print(f"[Test] Data received: {len(data)} items")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"[Test] Error: {res_cb.text}")

if __name__ == "__main__":
    test_cb_api()
