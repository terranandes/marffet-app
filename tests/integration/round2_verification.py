import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parents[2]
SCREENSHOT_DIR = os.path.join(BASE_DIR, 'tests', 'evidence')
BASE_URL = "http://127.0.0.1:3000"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot(page, name, is_mobile=False):
    prefix = "mobile" if is_mobile else "desktop"
    path = os.path.join(SCREENSHOT_DIR, f"round2_{name}_{prefix}.png")
    page.screenshot(path=path)
    print(f"📸 Saved {path}")

def run_round2():
    with sync_playwright() as p:
        print("🚀 Launching Browser...")
        browser = p.chromium.launch(headless=True)
        
        # --- DESKTOP ---
        print("\n🖥️ --- DESKTOP VERIFICATION ---")
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        # Login
        print("Logging in as terranfund mock...")
        page.goto(f"{BASE_URL}/", timeout=60000)
        # Call the new mock guest endpoint
        page.evaluate("fetch('/auth/guest', {method: 'POST'})")
        page.reload()
        page.wait_for_timeout(2000)
        
        # Area A: Landing
        page.goto(f"{BASE_URL}/", timeout=15000)
        take_screenshot(page, "area_a_landing")
        
        # Area B: Mars
        page.goto(f"{BASE_URL}/mars", timeout=15000)
        page.wait_for_selector("table", timeout=30000)
        take_screenshot(page, "area_b_mars_table")
        # Click row to show chart
        page.locator("tbody tr").first.click()
        page.wait_for_timeout(1500)
        take_screenshot(page, "area_b_mars_chart")
        
        # Area C: BCR
        page.goto(f"{BASE_URL}/race", timeout=15000)
        page.wait_for_timeout(3000)
        take_screenshot(page, "area_c_bcr_loaded")
        page.locator("button:has-text('Play')").first.click()
        page.wait_for_timeout(2000)
        take_screenshot(page, "area_c_bcr_playing")
        
        # Area D: Compound
        page.goto(f"{BASE_URL}/compound", timeout=15000)
        page.wait_for_timeout(2000)
        take_screenshot(page, "area_d_compound_single")
        # Click Compare
        compare_btn = page.locator("button:has-text('Comparison Mode')")
        if compare_btn.count() > 0:
            compare_btn.first.click()
            page.wait_for_timeout(1000)
        take_screenshot(page, "area_d_compound_compare")
        
        # Area E: Portfolio
        page.goto(f"{BASE_URL}/portfolio", timeout=15000)
        page.wait_for_timeout(3000)
        take_screenshot(page, "area_e_portfolio")
        
        # Area F: Trend & MyRace
        page.goto(f"{BASE_URL}/trend", timeout=15000)
        page.wait_for_timeout(2000)
        take_screenshot(page, "area_f_trend")
        
        page.goto(f"{BASE_URL}/myrace", timeout=15000)
        page.wait_for_timeout(3000)
        take_screenshot(page, "area_f_myrace")
        
        # Area G: CB Tab
        page.goto(f"{BASE_URL}/cb", timeout=15000)
        page.wait_for_timeout(2000)
        take_screenshot(page, "area_g_cb")
        
        # Area H: Modals
        # Try to open Settings Modal
        settings_btn = page.locator("button:has-text('Settings')").first
        if settings_btn.count() > 0:
            settings_btn.click()
            page.wait_for_timeout(1000)
            take_screenshot(page, "area_h_settings")
            # Close modal by pressing Escape
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)
            
        # Area I: AI Copilot
        copilot_fab = page.locator("button.fixed.bottom-6") # Usually bottom right FAB
        if copilot_fab.count() > 0:
            copilot_fab.first.click()
            page.wait_for_timeout(1000)
            take_screenshot(page, "area_i_copilot")
            # Close
            page.keyboard.press("Escape")
        
        # Area J: Admin Dashboard
        page.goto(f"{BASE_URL}/admin", timeout=15000)
        page.wait_for_timeout(2000)
        take_screenshot(page, "area_j_admin")
        
        context.close()
        
        # --- MOBILE ---
        print("\n📱 --- MOBILE VERIFICATION ---")
        mobile_context = browser.new_context(
            viewport={'width': 390, 'height': 844},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'
        )
        mpage = mobile_context.new_page()
        
        # Login
        mpage.goto(f"{BASE_URL}/", timeout=15000)
        mpage.evaluate("fetch('/auth/guest', {method: 'POST'})")
        mpage.reload()
        mpage.wait_for_timeout(2000)
        
        paths = ["/", "/portfolio", "/mars", "/compound", "/cb", "/trend", "/admin"]
        for p in paths:
            name = p.strip("/") or "home"
            mpage.goto(f"{BASE_URL}{p}", timeout=15000)
            mpage.wait_for_timeout(2000)
            take_screenshot(mpage, f"area_{name}", is_mobile=True)
            
        mobile_context.close()
        browser.close()
        print("\n✅ Round 2 UI Verification Script Complete!")

if __name__ == "__main__":
    run_round2()
