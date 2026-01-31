import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from playwright.sync_api import sync_playwright, expect
import time
import os
import json

# Setup
screenshots_dir = '/home/terwu01/.gemini/antigravity/brain/1f67aed8-cf82-47ed-9aaa-a43a86a43af7'
base_url = 'http://localhost:3000'

def run_bug_hunt():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print("\n🐞 Starting Bug Hunt Verification Suite...\n")

        # ----------------------------------------------------------------
        # Test 1: Settings Modal (Guest Access)
        # ----------------------------------------------------------------
        print("🔍 [Test 1] Verifying Settings Modal (Region Lock)...")
        try:
            page.goto(base_url)
            page.evaluate("localStorage.clear()") # Clear state
            page.reload()

            # Find Settings Gear Icon using Title attribute
            settings_btn = page.locator('button[title="Settings"]').first
            
            if settings_btn.is_visible():
                print("   Found Settings button. Clicking...")
                settings_btn.click()
                
                # Check Modal Content
                page.wait_for_selector('text=App Preferences', timeout=5000)
                
                # Check Region Select
                region_select = page.locator('select').first 
                
                is_disabled = region_select.is_disabled()
                value = region_select.input_value()
                
                print(f"   Region Select: Disabled={is_disabled}, Value={value}")
                
                if is_disabled and value == "TW":
                    print("✅ Settings Modal Verified: Region locked to Taiwan.")
                else:
                    print("❌ Settings Modal FAILED: Region not locked correctly.")
                
                # Close Modal
                page.keyboard.press('Escape')
            else:
                print("⚠️ Settings button not found on Home page (Guest).")
                page.screenshot(path=f'{screenshots_dir}/debug_settings_missing.png')

        except Exception as e:
            print(f"❌ [Test 1] Failed: {e}")
            page.screenshot(path=f'{screenshots_dir}/fail_settings.png')

        # ----------------------------------------------------------------
        # Test 2: BCR Start Year (The "2017" Bug)
        # ----------------------------------------------------------------
        print("\n🔍 [Test 2] Verifying BCR Default Start Year...")
        try:
            # 1. Clear LocalStorage to simulate fresh visit
            page.goto(f'{base_url}/race')
            page.evaluate("localStorage.clear()")
            page.evaluate("sessionStorage.clear()")
            page.reload()
            
            # 2. Wait for loading (Increased timeout for backend restart)
            page.wait_for_selector('text=Bar Chart Race', timeout=15000)
            
            print("   Analyzing API Requests...")
            # Capture the API request for data
            with page.expect_request(lambda request: "race-data" in request.url, timeout=15000) as first_req:
                # Trigger a data fetch or wait if it already happened?
                # Reload to be sure we catch it
                page.reload()
            
            req_url = first_req.value.url
            print(f"   API Request URL: {req_url}")
            
            if "start_year=2006" in req_url:
                print("✅ Frontend requested start_year=2006 (Correct Default).")
            elif "start_year=2017" in req_url:
                print("❌ Frontend requested start_year=2017 (Incorrect Default).")
            else:
                print(f"⚠️ Unexpected Request Parameters: {req_url}")

        except Exception as e:
            print(f"❌ [Test 2] Failed: {e}")
            page.screenshot(path=f'{screenshots_dir}/fail_bcr.png')

        # ----------------------------------------------------------------
        # Test 3: Mars Strategy Inputs
        # ----------------------------------------------------------------
        print("\n🔍 [Test 3] Verifying Mars Strategy Inputs...")
        try:
            page.goto(f'{base_url}/mars')
            page.evaluate("localStorage.clear()") # Ensure clean state
            page.evaluate("sessionStorage.clear()")
            page.reload()
            page.wait_for_selector('text=Mars Strategy', timeout=10000)
            
            # Check Start Year Input
            start_year_input = page.locator('input[type="number"]').first
            val = start_year_input.input_value()
            print(f"   Mars Start Year Input Value: {val}")
            
            if val == "2006":
                print("✅ Mars Page defaults to 2006.")
            else:
                print(f"❌ Mars Page defaults to {val} (Expected 2006).")
                
        except Exception as e:
            print(f"❌ [Test 3] Failed: {e}")
            page.screenshot(path=f'{screenshots_dir}/fail_mars.png')

        print("\n🎉 Bug Hunt Complete.")
        browser.close()

if __name__ == "__main__":
    run_bug_hunt()
