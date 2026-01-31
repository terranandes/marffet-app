import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def check(url, desc, expected_code=200):
    print(f"Testing {desc} ({url})...", end=" ")
    try:
        r = requests.get(url)
        if r.status_code == expected_code:
            print(f"✅ OK ({r.status_code})")
            return True
        else:
            print(f"❌ FAILED ({r.status_code})")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def run():
    print("⏳ Waiting for backend...")
    for _ in range(10):
        try:
            if requests.get(BASE_URL).status_code == 200:
                print("🚀 Backend is UP!")
                break
        except:
            time.sleep(1)
    else:
        print("❌ Backend failed to start.")
        sys.exit(1)

    # 1. Home Page
    if not check(BASE_URL, "Home Page"):
        sys.exit(1)

    # 2. Leaderboard API
    # Assuming endpoint is /api/leaderboard based on code context
    check(f"{BASE_URL}/api/leaderboard", "Leaderboard API")

    # 3. Public Profile (Test with 'default' or a known user if possible)
    # Finding a user from leaderboard first
    try:
        r = requests.get(f"{BASE_URL}/api/leaderboard")
        data = r.json()
        if data and len(data) > 0:
            user_id = data[0]['user_id']
            print(f"🔍 Found User: {user_id}")
            check(f"{BASE_URL}/api/public/profile/{user_id}", f"Public Profile ({user_id})")
        else:
            print("⚠️ Leaderboard empty, skipping Profile check.")
    except Exception as e:
        print(f"⚠️ Could not fetch leaderboard for profile check: {e}")

    print("\n✅ API Verification Complete (Headless)")

if __name__ == "__main__":
    run()
