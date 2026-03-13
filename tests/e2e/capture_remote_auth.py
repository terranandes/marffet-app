import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Default targets
TARGET_URL = os.getenv("TARGET_URL", "https://marffet-app.zeabur.app")
ACCOUNT_TIER = os.getenv("ACCOUNT_TIER", "gm").lower()

STATE_DIR = os.path.join(BASE_DIR, ".worktrees", "auth_states")
if not os.path.exists(STATE_DIR):
    os.makedirs(STATE_DIR)

# Which file to save to based on tier
STATE_FILE = os.path.join(STATE_DIR, f"state_{ACCOUNT_TIER}.json")

print(f"🌍 Target URL: {TARGET_URL}")
print(f"👤 Capturing State for Tier: {ACCOUNT_TIER.upper()}")
print(f"💾 Will save to: {STATE_FILE}")
print("-" * 50)
print("INSTRUCTIONS:")
print("1. A visible browser window will open.")
print("2. It will navigate to the login page.")
print("3. Log into Google with the corresponding account.")
print("4. Wait until you are fully redirected back to the portfolio page.")
print(f"   (You should see your account name/tier in the sidebar)")
print("5. The browser will automatically close once logged in, saving the state.")
print("-" * 50)
input("Press Enter to launch browser...")

with sync_playwright() as p:
    # We use standard Chromium but disable automation flags to bypass Google's security
    browser = p.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    # 1. Navigate to the App
    page.goto(TARGET_URL)

    # 2. Wait for user to navigate the Google Login flow
    # We wait until the application loads the logged-in portfolio view.
    # We use a long timeout because human login + 2FA takes time.
    print("\n⏳ Browser open. Please log in now...")
    
    # Wait for the "Sign In" button to disappear or the account menu to appear.
    # An easy check is that the "Explore as Guest" button is gone, or a personalized setting exists.
    # Alternative generic check: Wait until we are back on the target domain and network is idle.
    
    try:
        # Give the user 5 minutes to complete auth
        # We wait for the sidebar profile section or something indicative of success
        page.wait_for_url(f"**/portfolio**", timeout=300000) # 5 minutes
        page.wait_for_load_state('networkidle', timeout=15000)
        
        # Adding a small buffer to ensure the backend session cookie is firmly set
        page.wait_for_timeout(3000)
        
        # 3. Save State
        context.storage_state(path=STATE_FILE)
        print(f"\n✅ SUCCESS! Authentication state saved to: {STATE_FILE}")
        print(f"   You can now run E2E tests using this state.")
        print(f"   Example: AUTH_STATE={STATE_FILE} TARGET_URL={TARGET_URL} uv run python tests/e2e/e2e_suite.py")

    except Exception as e:
        print(f"\n❌ FAILED. Did not detect successful login within 5 minutes.")
        print(f"   Error: {e}")
        
    finally:
        browser.close()
