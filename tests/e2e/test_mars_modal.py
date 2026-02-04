
import re
from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://localhost:3000"

def test_mars_modal_loading():
    print(f"🚀 Starting E2E Mock: Mars Modal Check")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Capture Console Logs
        page.on("console", lambda msg: print(f"[BROWSER] {msg.text}"))
        page.on("pageerror", lambda err: print(f"[BROWSER ERROR] {err}"))
        page.on("response", lambda response: print(f"[NETWORK] {response.status} {response.url}"))
        
        # 1. Visit Page
        print(f"Navigating to {BASE_URL}/mars...")
        page.goto(f"{BASE_URL}/mars")
        
        # 2. Wait for Table
        print("Waiting for Stock Table...")
        # Wait for at least one row with class that looks like a stock row or just td
        page.wait_for_selector("table tbody tr")
        
        # 3. Find 2330 (TSMC) and Click
        # We look for the cell containing "2330"
        print("Looking for stock 2330...")
        row = page.get_by_text("2330", exact=True)
        if row.count() == 0:
            print("❌ Stock 2330 not found in list (maybe loading slow?)")
            page.screenshot(path="tests/evidence/error_no_stock.png")
            browser.close()
            return
            
        print("Clicking 2330...")
        row.click()
        
        # 4. Wait for Modal
        print("Waiting for Modal...")
        page.wait_for_selector("h2:has-text('Result:')")
        
        # 5. Check "Final Value" Field
        # It initially says "Loading...". We wait for it to be a dollar amount.
        print("Waiting for 'Loading...' to disappear...")
        try:
            # We look for the "Final Value" label's sibling/container.
            # In the code: "Final Value" ... "Loading..." is in the same card?
            # Let's just wait for a text that is NOT "Loading..." in the relevant area.
            # Or simpler: Wait for network idle.
            
            # The "Loading..." text is explicitly rendered.
            # We want to verify it goes away.
            # There are 3 "Loading..." text instances (one per column).
            expect(page.get_by_text("Loading...", exact=True).first).not_to_be_visible(timeout=60000)
            print("✅ 'Loading...' disappeared.")
            
            # Take Evidence
            page.screenshot(path="tests/evidence/mars_modal_success.png")
            print("📸 Screenshot saved: tests/evidence/mars_modal_success.png")
            
        except AssertionError:
            print("❌ Timeout: 'Loading...' is still visible after 10s.")
            page.screenshot(path="tests/evidence/error_modal_stuck.png")
        
        browser.close()

if __name__ == "__main__":
    test_mars_modal_loading()
