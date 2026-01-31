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

BASE_URL = "https://martian-api.zeabur.app"
# BASE_URL = "http://localhost:8000"

def debug_stock_name():
    print(f"📡 Connecting to {BASE_URL}...")
    
    # 1. Guest Login
    session = requests.Session()
    res = session.post(f"{BASE_URL}/auth/guest")
    if res.status_code != 200:
        print(f"❌ Login failed: {res.text}")
        return

    print("✅ Guest Login Successful")
    
    # 2. Get Groups (to find default group)
    res = session.get(f"{BASE_URL}/api/portfolio/groups")
    groups = res.json()
    if not groups:
        print("❌ No groups found")
        return
    
    group_id = groups[0]['id']
    print(f"📂 Using Group ID: {group_id}")
    
    # 2b. Add Stock 2330 (Control)
    print("➕ Adding Stock 2330 (Control)...")
    payload_2330 = {
        "group_id": group_id,
        "stock_id": "2330",
        "shares": 0, "cost": 0, "date": "2026-01-20"
    }
    res = session.post(f"{BASE_URL}/api/portfolio/target", json=payload_2330)
    if res.status_code == 200:
        print(f"✅ 2330 Added: {json.dumps(res.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ 2330 Failed: {res.text}")

    # 3. Add Stock 6533
    stock_id = "6533"
    print(f"➕ Adding Stock {stock_id}...")
    payload_6533 = {
        "group_id": group_id,
        "stock_id": stock_id,
        "shares": 0, "cost": 0, "date": "2026-01-20"
    }
    res = session.post(f"{BASE_URL}/api/portfolio/target", json=payload_6533)
    
    if res.status_code == 200:
        data = res.json()
        print(f"✅ 6533 Added: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"⚠️ 6533 Failed: {res.text}")

    # 4. Fetch Group Details
    print("🔍 Fetching Group Details...")
    res = session.get(f"{BASE_URL}/api/portfolio/group/{group_id}")
    group_data = res.json()
    
    # Check both
    for sid in ["2330", "6533"]:
        found = False
        for target in group_data.get('targets', []):
            if target['stock_id'] == sid:
                found = True
                print(f"🎯 Stock {sid} Name in DB: '{target.get('stock_name')}'")
                break
        if not found:
            print(f"❌ Stock {sid} not found in group targets.")

if __name__ == "__main__":
    debug_stock_name()
