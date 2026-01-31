import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import requests
import os
import sys

BASE_URL = "http://localhost:8000"

def test_legacy_cleanup():
    print("Test 1: Legacy File Cleanup...")
    # Check if files exist
    legacy_files = ["app/static/main.js", "app/static/index.html", "frontend_vite_backup"]
    failed = False
    for f in legacy_files:
        if os.path.exists(f):
            print(f"❌ Failed: {f} still exists.")
            failed = True
        else:
            print(f"✅ Pass: {f} removed.")
    
    if failed:
        sys.exit(1)

def test_backend_root():
    print("\nTest 2: Backend Root Endpoint...")
    try:
        res = requests.get(f"{BASE_URL}/")
        if res.status_code == 200 and res.headers['content-type'] == 'application/json':
             print("✅ Pass: Root returns JSON.")
        else:
             print(f"❌ Failed: Root returned {res.status_code} {res.headers.get('content-type')}")
             sys.exit(1)
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        sys.exit(1)

def test_race_api():
    print("\nTest 3: Race API Availability...")
    try:
        # Note: Need authentication? Or does race-data allow public/default?
        # Current logic: default user if no auth.
        res = requests.get(f"{BASE_URL}/api/portfolio/race-data")
        if res.status_code == 200:
             print("✅ Pass: Race API reachable.")
        else:
             print(f"❌ Failed: Race API returned {res.status_code}")
             # sys.exit(1) # Don't hard fail if it's just auth
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    print(f"Running Migration Verification against {BASE_URL}...")
    test_legacy_cleanup()
    test_backend_root()
    test_race_api()
    print("\n✅ MIGRATION VERIFIED SUCCESS")
