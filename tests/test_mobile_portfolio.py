from playwright.sync_api import sync_playwright
import time
import os

# Configuration
BASE_URL = os.getenv("TARGET_URL", "http://localhost:3000")
SCREENSHOT_DIR = '/home/terwu01/.gemini/antigravity/brain/b49fbb77-9d9c-4a6f-b522-53f3e307f306/evidence'

print(f"🎯 Target URL: {BASE_URL}")
print(f"📸 Evidence Dir: {SCREENSHOT_DIR}")

if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

def run_mobile_test():
    with sync_playwright() as p:
        print("🚀 Launching Mobile Browser (iPhone 12 Viewport)...")
        browser = p.chromium.launch(headless=True)
        # iPhone 12 Viewport
        context = browser.new_context(viewport={'width': 390, 'height': 844})
        page = context.new_page()

        try:
            print(f"🔗 Header: Checking {BASE_URL}/portfolio")
            
            # 1. Navigation & Guest Login
            page.goto(f'{BASE_URL}/')
            
            # Click "Continue as Guest" if on Landing
            # landing_guest_btn = page.get_by_role("button", name="Continue as Guest").first
            # If sidebar is hidden, this fails. App handles it.
            pass
            # if landing_guest_btn.is_visible():
            #      landing_guest_btn.click(force=True)
            #      time.sleep(1)

            page.goto(f'{BASE_URL}/portfolio')
            # Removed networkidle which can hang on polling
            # page.wait_for_load_state('networkidle')
            time.sleep(2) # Simple wait for load
            
            # Handle "Continue as Guest" if shown on Portfolio page
            # Note: On Mobile, the sidebar button is hidden. 
            # The app automatically switches to Guest Mode on 401, so explicit click is not needed.
            try:
                guest_btn = page.get_by_role("button", name="Continue as Guest").first
                if guest_btn.is_visible():
                     # Only click if actually in viewport (e.g. if we were on desktop or added a mobile button)
                     # For now, we skip to avoid "outside viewport" error on hidden sidebar
                     pass
            except:
                pass
            
            time.sleep(1)

            # 2. Setup: Create Group and Add Stock for Testing
            # Check if we need to create a group
            # Wait for groups to load
            time.sleep(2)
            
            needs_group = False
            if page.get_by_text("Start Your Portfolio").is_visible() or page.get_by_text("No groups yet").is_visible():
                needs_group = True
            
            if needs_group:
                print("   Creating Test Group...")
                # Ensure + New Group is visible
                new_group_btn = page.locator("button", has_text="+ New Group")
                if new_group_btn.is_visible():
                    new_group_btn.click()
                else:
                    # Maybe icon version on mobile? No, text is "+ New Group" in JSX
                    print("⚠️ Cannot find + New Group button")
                
                page.get_by_placeholder("Group name...").fill("Mobile Test")
                page.get_by_role("button", name="Create").click()
                # Wait for creation - Wait for the TAB button
                page.locator("button", has_text="Mobile Test").first.wait_for(state="visible", timeout=5000)
            
            # Select group
            print("   Selecting Group 'Mobile Test'...")
            group_tab = page.locator("button", has_text="Mobile Test").first
            if group_tab.is_visible():
                group_tab.click()
            else:
                print("❌ Group 'Mobile Test' tab not found!")
            
            time.sleep(1) # Wait for state update

            # Add Stock
            print("   Adding Stock 2330...")
            # Wait for input to be visible
            stock_input = page.get_by_placeholder("Stock ID (e.g. 2330)")
            stock_input.wait_for(state="visible", timeout=5000)
            stock_input.fill("2330")
            page.get_by_placeholder("Name (e.g. 台積電)").fill("TSMC")
            page.get_by_text("+ Add Stock").click()
            time.sleep(2) # Wait for add

            # 3. Verification - MOBILE VIEW
            print("\n📱 VERIFICATION: Mobile Layout")
            
            # Check Table is HIDDEN
            # Using CSS selector for table and checking visibility
            # Note: Playwright .is_visible() checks bounding box. 
            # If parent div is hidden, verify that.
            # Next.js implementation wraps table in 'hidden lg:block'
            # We check if the table element itself is visible in this viewport
            table_visible = page.locator("table").first.is_visible()
            if not table_visible:
                print("✅ Table View is HIDDEN (Correct)")
            else:
                print("❌ Table View is VISIBLE (Incorrect)")

            # Check Card is VISIBLE
            # The card header contains "TSMC" and market value
            # We look for the card container.
            # In our implementation, card is div with class "bg-white/5 border border-white/10 rounded-xl"
            # Let's find by text in header
            print("   Waiting for 'TSMC' card to appear...")
            try:
                # Use a more specific locator for the card content or wait for it
                page.locator("div").filter(has_text="TSMC").first.wait_for(state="visible", timeout=5000)
                print("✅ Mobile Card is VISIBLE")
            except:
                print("❌ Mobile Card NOT found (Timeout)")
                page.screenshot(path=f'{SCREENSHOT_DIR}/mobile_card_missing.png')
            
            page.screenshot(path=f'{SCREENSHOT_DIR}/mobile_1_card_view.png')

            # 4. Interaction - Expand Card
            print("\n👆 VERIFICATION: Expand Card")
            
            # Check if details hidden initially (e.g. "Shares", "Avg Cost")
            # "Shares" label is in the expanded details
            if page.get_by_text("Shares", exact=True).count() == 0 or not page.get_by_text("Shares", exact=True).first.is_visible():
                 print("✅ Details initially hidden")
            else:
                 print("⚠️ Details visible before click (might be expanded default?)")

            # Click header to expand
            print("   Clicking 'TSMC' text to expand...")
            # We click the element containing "TSMC"
            # card_header.click() # This might be the container which absorbs click?
            page.get_by_text("TSMC", exact=True).first.click()
            time.sleep(1)
            
            # Check details visible
            if page.get_by_text("Shares", exact=True).first.is_visible():
                print("✅ Card Expanded: Details Visible")
            else:
                print("❌ Card Did Not Expand")

            page.screenshot(path=f'{SCREENSHOT_DIR}/mobile_2_expanded.png')

            # 5. Check Action Buttons
            print("\n🔘 VERIFICATION: Action Buttons")
            if page.get_by_role("button", name="➕ Add Tx").is_visible():
                print("✅ 'Add Tx' Button Visible")
            else:
                print("❌ 'Add Tx' Button Missing")

            if page.get_by_role("button", name="📜 History").is_visible():
                print("✅ 'History' Button Visible")
            else:
                 print("❌ 'History' Button Missing")

        except Exception as e:
            print(f"💥 Error: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path=f'{SCREENSHOT_DIR}/mobile_error.png')
        
        finally:
            browser.close()
            print("🏁 Mobile Test Complete")

if __name__ == "__main__":
    run_mobile_test()
