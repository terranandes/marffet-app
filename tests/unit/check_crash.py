import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


import sys
import os
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_routes():
    print("[-] Checking /auth/guest...")
    try:
        resp = client.post("/auth/guest")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"[FAIL] /auth/guest crashed: {e}")

    print("\n[-] Checking /auth/login...")
    try:
        # This will try to redirect to Google. TestClient follows redirects by default? 
        # Actually authorize_redirect returns 200 HTML with JS redirect in our implementation.
        resp = client.get("/auth/login", follow_redirects=False) 
        print(f"Status: {resp.status_code}")
        # print(f"Content: {resp.text[:100]}...") # Verify HTML content
    except Exception as e:
        print(f"[FAIL] /auth/login crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_routes()
