from playwright.sync_api import sync_playwright
import time
import os

SCREENSHOT_DIR = '/home/terwu01/.gemini/antigravity/brain/1f67aed8-cf82-47ed-9aaa-a43a86a43af7/evidence'
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

def verify_alignment():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        
        # ------------------------------------------------------------------
        # 1. LEGACY UI CHECK (Port 8000)
        # ------------------------------------------------------------------
        print("\n🔍 Checking LEGACY UI (http://127.0.0.1:8000)...")
        page_legacy = context.new_page()
        try:
            page_legacy.goto("http://127.0.0.1:8000", timeout=30000)
            page_legacy.wait_for_selector("text=My Portfolio", timeout=15000)
            
            # Ensure at least one transaction exists to check colors
            # Only if table is empty?
            if page_legacy.locator("tbody tr").count() <= 1: # Header + Empty msg
                 # Add dummy transaction
                 print("   Adding dummy Buy transaction...")
                 page_legacy.get_by_text("+ Add Stock").click() # Or logic to add tx
                 # Legacy "Add Stock" is actually for adding stock target.
                 # "New Transaction" is usually via some other button or inside the stock row?
                 # Actually legacy index.html shows transaction history is for whole portfolio or specific?
                 # It seems it's global or per stock.
                 
                 # Let's try adding a stock '1101' if needed to test
                 # But let's assume Portfolio populated from `portfolio.db`
                 pass
            
            # Open Transaction History (Global or per stock)
            # The previous grep showed "Transaction History Modal"
            # How to trigger? 
            # Looking at index.html: `<button @click="showTxHistory = true" ...`
            # Is there a button visible? "📜 History"?
            # Let's look for a button with text "History" or similar.
            
            # If we can't find it easily, we check the STOCK ROW badge if it exists?
            # Wait, line 1046 index.html was in `txHistory` loop.
            # This modal seems to be triggered by "showTxHistory".
            # The button for it might be in the sidebar or navbar?
            pass

            page_legacy.screenshot(path=f'{SCREENSHOT_DIR}/legacy_dashboard.png')
            print("   📸 Legacy Dashboard captured")
            
        except Exception as e:
            print(f"❌ Legacy UI Error: {e}")

        # ------------------------------------------------------------------
        # 2. NEXT.JS UI CHECK (Port 3000)
        # ------------------------------------------------------------------
        print("\n🔍 Checking NEXT.JS UI (http://127.0.0.1:3000)...")
        page_next = context.new_page()
        try:
            # Login as Guest first for Next.js to ensure session
            page_next.goto("http://127.0.0.1:3000", timeout=60000)
            page_next.wait_for_selector("text=Continue as Guest", timeout=10000)
            page_next.get_by_text("Continue as Guest").click()
            page_next.wait_for_selector("text=Sign Out", timeout=15000)

            # Go to Portfolio
            page_next.goto("http://localhost:3000/portfolio", timeout=90000) # Long timeout for compile
            page_next.wait_for_selector("text=Market Value", timeout=60000)
            
            page_next.screenshot(path=f'{SCREENSHOT_DIR}/nextjs_portfolio.png')
            print("   📸 Next.js Portfolio captured")
            
            # Check for similarities
            if page_next.get_by_text("My Portfolio").count() > 0:
                print("   ✅ Header matched: 'My Portfolio'")
            else:
                print("   ⚠️ Header mismatch or not found")

            # ------------------------------------------------------------------
            # 3. AI COPILOT CHECK
            # ------------------------------------------------------------------
            print("\n🤖 Checking AI Copilot Default Key Logic...")
            
            # Check /auth/me payload
            auth_me = page_next.evaluate("async () => await fetch('/auth/me').then(r => r.json())")
            print(f"   ℹ️ /auth/me Response: {auth_me}")
            
            has_server_key = auth_me.get('has_gemini_key', False)
            print(f"   ℹ️ has_gemini_key: {has_server_key}")
            
            # Open Chat
            page_next.locator("button[title='Open AI Copilot']").click()
            page_next.wait_for_selector("text=Mars AI Copilot", timeout=5000)
            
            # Check Input visibility
            # Logic: If has_server_key is True, Input should be HIDDEN.
            # Input placeholder: "Enter Gemini API Key..."
            input_count = page_next.get_by_placeholder("Enter Gemini API Key...").count()
            
            if has_server_key:
                if input_count == 0:
                    print("   ✅ Input HIDDEN (Correct behavior for Default Key)")
                else:
                    print("   ❌ Input VISIBLE despite Default Key (Fail)")
            else:
                 if input_count > 0:
                    print("   ✅ Input VISIBLE (Correct behavior for Missing Key)")
                 else:
                    print("   ❌ Input HIDDEN despite Missing Key (Fail)")

        except Exception as e:
            print(f"❌ Next.js UI Error: {e}")
            page_next.screenshot(path=f'{SCREENSHOT_DIR}/nextjs_error.png')

        browser.close()

if __name__ == "__main__":
    verify_alignment()
