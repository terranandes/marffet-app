import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from playwright.sync_api import sync_playwright
import time
import os
import re

# Configuration
BASE_URL = os.getenv("TARGET_URL", "http://localhost:3000")
SCREENSHOT_DIR = os.path.join(BASE_DIR, 'tests', 'evidence')

print(f"🎯 Target URL: {BASE_URL}")
print(f"📸 Evidence Dir: {SCREENSHOT_DIR}")

if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

def run_mobile_test():
    print("🚀 Launching Mobile Browser (iPhone 12 Viewport)...")
    
    # Check what URL to test against
    target_url = os.environ.get("TARGET_URL", "http://localhost:3000").replace("localhost", "127.0.0.1")
    BASE_URL = target_url

    print(f"🎯 Target URL: {BASE_URL}")
    print(f"🔗 Header: Checking {BASE_URL}/portfolio")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # iPhone 12 Viewport
        context = browser.new_context(viewport={'width': 390, 'height': 844})
        page = context.new_page()

        try:
            
            # 1. Navigation & Guest Login
            print("   Navigating to Portfolio...")
            page.goto(f"{BASE_URL}/portfolio", wait_until="domcontentloaded", timeout=120000)
            
            # Hide Next.js dev overlay which intercepts clicks on mobile viewports
            page.add_style_tag(content="nextjs-portal { display: none !important; }")
            
            # Simple wait for hydration
            page.wait_for_timeout(3000)

            # Click "Explore as Guest" button
            print("   Waiting for Explore as Guest button...")
            try:
                # Support both English and Traditional Chinese
                guest_btn = page.locator('button:visible', has_text=re.compile(r"Explore as Guest|以訪客身分探索")).first
                guest_btn.wait_for(state="visible", timeout=5000)
                print(f"   Clicking Explore as Guest button ({guest_btn.inner_text()})...")
                guest_btn.click(timeout=5000) # removed force=True to ensure actionability
                page.wait_for_timeout(3000) # Wait for local state to update
            except Exception as e:
                print(f"   ⚠️ Guest button click intercepted/timed out: {e}")
                
            # Verify locally and fallback
            guest_mode = page.evaluate("() => localStorage.getItem('marffet_guest_mode')")
            print(f"   [DEBUG] localStorage marffet_guest_mode = {guest_mode}")
            
            # Use javascript click if normal click failed, or just set storage
            if guest_mode != "true":
                print("   [DEBUG] guest mode was not set. Forcing evaluation.")
                page.evaluate("() => { localStorage.setItem('marffet_guest_mode', 'true'); window.location.reload(); }")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(3000)

            # Now we should be on the portfolio page
            print("   Verifying Portfolio Page...")
            page.wait_for_load_state('networkidle', timeout=15000)

            # 2. Setup: Create Group and Add Stock for Testing
            # Check if we need to create a group
            # Wait for groups to load
            print("   Checking for existing group...")
            time.sleep(2)
            needs_group = False
            if page.locator("button", has_text="Mobile Test").count() == 0:
                needs_group = True
            
            if needs_group:
                print("   Creating Test Group...")
                # Find and click "+ New Group" button in PortfolioHeader
                # Support both English and Traditional Chinese
                new_group_btn = page.locator('button', has_text=re.compile(r"\+ (New Group|新群組)")).first
                try:
                    new_group_btn.wait_for(state="visible", timeout=15000)
                    new_group_btn.scroll_into_view_if_needed()
                    new_group_btn.click()
                except Exception as e:
                    print("   [DEBUG] + New Group not found. Taking diagnostic screenshot.")
                    page.screenshot(path=f'{SCREENSHOT_DIR}/debug_new_group_timeout.png')
                    with open(f"{SCREENSHOT_DIR}/debug_body.html", "w") as f:
                        f.write(page.content())
                    raise e
                
                group_name_input = page.get_by_placeholder("Group name...")
                group_name_input.wait_for(state="visible", timeout=5000)
                group_name_input.press_sequentially("Mobile Test", delay=50)
                page.wait_for_timeout(500)
                # Ensure the field has focus and press Enter
                group_name_input.focus()
                page.keyboard.press("Enter")
                page.wait_for_timeout(4000) # Wait for creation to propagate
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, "debug_after_group_create.png"))
                
                # Wait for creation - Wait for the TAB button
                try:
                    page.locator("button", has_text="Mobile Test").first.wait_for(state="visible", timeout=10000)
                except Exception as e:
                    print("   [DEBUG] Parsing HTML to file after Group Creation timeout...")
                    with open(f"{SCREENSHOT_DIR}/debug_body.html", "w") as f:
                        f.write(page.locator("body").inner_html())
                    raise e
            
            # Select group
            print("   Selecting Group 'Mobile Test'...")
            # Use filter to get the exact tab div/button and avoid the remove 'x' button
            group_tab = page.locator('button', has_text="Mobile Test").first
            group_tab.scroll_into_view_if_needed()
            group_tab.click()
            
            time.sleep(1) # Wait for state update

            # Add Stock
            print("   Adding Stock 2330...")
            # Wait for input to be visible
            stock_input = page.get_by_placeholder("Ticker (e.g. 2330)")
            stock_input.wait_for(state="visible", timeout=5000)
            stock_input.fill("2330")
            page.get_by_placeholder(re.compile(r"Name|名稱")).fill("TSMC")
            # Support both English and Chinese for Add Asset
            page.locator("button", has_text=re.compile(r"\+ (Add Asset|新增資產)")).first.click()
            time.sleep(3) # Wait for add

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

            # Check Bottom Tab Bar is VISIBLE
            tab_bar_visible = page.locator('[data-testid="bottom-tab-bar"]').is_visible()
            if tab_bar_visible:
                print("✅ Bottom Tab Bar is VISIBLE")
            else:
                print("❌ Bottom Tab Bar is HIDDEN (Incorrect)")

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
            if page.get_by_text("Shares").count() == 0 or not page.get_by_text("Shares").first.is_visible():
                 print("✅ Details initially hidden")
            else:
                 print("⚠️ Details visible before click (might be expanded default?)")

            # Click header to expand
            print("   Clicking 'TSMC' text to expand...")
            # Be more aggressive about finding the clickable card header
            # The card has 'onClick' on the padding div
            page.locator(".cursor-pointer").filter(has_text="TSMC").first.click()
            page.wait_for_timeout(1000)
            
            # Check details visible
            if page.get_by_text("Shares").first.is_visible():
                print("✅ Card Expanded: Details Visible")
            else:
                print("❌ Card Did Not Expand")

            page.screenshot(path=f'{SCREENSHOT_DIR}/mobile_2_expanded.png')

            # 5. Check Action Buttons
            print("\n🔘 VERIFICATION: Action Buttons")
            if page.get_by_role("button", name="✚ Trade").is_visible():
                print("✅ 'Trade' Button Visible")
            else:
                print("❌ 'Trade' Button Missing")

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
