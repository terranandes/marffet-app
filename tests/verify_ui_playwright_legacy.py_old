from playwright.sync_api import sync_playwright
import time

def run():
    print("🚀 Starting Playwright Verification...")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 1. Navigate
            print("Navigating to http://localhost:8000...")
            page.goto("http://localhost:8000")
            page.wait_for_load_state("networkidle")
            print(f"Page Title: {page.title()}")
            
            # 2. Check Console Errors
            # (We can't easily capture past logs in sync mode unless we subscribe, 
            # but we can check for current state)
            
            # 3. Click TSMC (2330)
            # Find element with text '2330' or class
            print("Clicking TSMC (2330)...")
            # Assuming the list renders, we click the row. 
            # We need a robust selector. Let's try text.
            page.get_by_text("2330").first.click()
            
            # 4. Verify Modal
            # Wait for modal header
            page.wait_for_selector("text=Result:", timeout=5000)
            print("Modal Opened.")
            
            # 5. Check Tabs
            # Look for "Wealth" and "Dividend" buttons
            if page.get_by_role("button", name="Wealth").is_visible():
                print("✅ Wealth Tab Found")
            else:
                print("❌ Wealth Tab MISSING")
                
            if page.get_by_role("button", name="Dividend").is_visible():
                print("✅ Dividend Tab Found")
            else:
                print("❌ Dividend Tab MISSING")
                
            # 6. Switch Tab
            print("Switching to Dividend Tab...")
            page.get_by_role("button", name="Dividend").click()
            time.sleep(1)
            
            # Verify Chart Header changed
            if page.get_by_text("Yearly Cash Div. Received").is_visible():
                print("✅ Chart Title Updated to 'Yearly Cash Div. Received'")
            else:
                print("❌ Chart Title update FAILED")
                
            browser.close()
            print("🎉 Verification Complete!")
            
        except Exception as e:
            print(f"💥 Verification Failed: {e}")

if __name__ == "__main__":
    run()
