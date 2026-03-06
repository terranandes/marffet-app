import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("TARGET_URL", "http://localhost:3000")
SCREENSHOT_DIR = os.path.join(BASE_DIR, 'tests', 'evidence')

if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

def run_phase31_tests():
    with sync_playwright() as p:
        print(f"🎯 Target URL: {BASE_URL}")
        browser = p.chromium.launch(headless=True)
        
        # Desktop Context
        desktop_context = browser.new_context(viewport={'width': 1280, 'height': 800})
        desktop_page = desktop_context.new_page()
        
        # Mobile Context (iPhone 12)
        mobile_context = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        mobile_page = mobile_context.new_page()
        
        try:
            print("\n🛑 TEST: Desktop Sidebar User Profile (Regression Fix)")
            desktop_page.goto(f'{BASE_URL}/portfolio')
            desktop_page.wait_for_load_state('domcontentloaded')
            
            # Look for Guest or Sign In buttons scoped to the desktop sidebar (aside element)
            try:
                sidebar = desktop_page.locator("aside").first
                sidebar.wait_for(state="visible", timeout=5000)
                
                # Wait for React hydration and loading skeleton to disappear
                desktop_page.wait_for_timeout(3000)
                
                # Wait for loading skeleton to be gone (the animate-pulse element)
                try:
                    desktop_page.locator("aside .animate-pulse").wait_for(state="hidden", timeout=10000)
                except:
                    pass  # May not be loading at all
                
                # Additional wait for user state to resolve
                desktop_page.wait_for_timeout(2000)
                
                # Check for Sign In or Guest or Sign Out within the sidebar only
                sidebar_signin = sidebar.get_by_text("Sign In with Google")
                sidebar_guest = sidebar.get_by_text("Explore as Guest")
                sidebar_signout = sidebar.get_by_text("Sign Out")
                
                found = False
                for label, loc in [("Sign In with Google", sidebar_signin), ("Explore as Guest", sidebar_guest), ("Sign Out", sidebar_signout)]:
                    if loc.count() > 0 and loc.first.is_visible():
                        print(f"✅ Sidebar User Profile found: '{label}' visible.")
                        found = True
                        break
                
                if not found:
                    # Take a debug screenshot before failing
                    desktop_page.screenshot(path=f'{SCREENSHOT_DIR}/desktop_sidebar_debug_state.png')
                    raise Exception("No user profile buttons visible in sidebar aside")
                
                desktop_page.screenshot(path=f'{SCREENSHOT_DIR}/desktop_sidebar_fixed.png')
            except Exception as e:
                print("❌ Sidebar User Profile buttons missing!")
                desktop_page.screenshot(path=f'{SCREENSHOT_DIR}/desktop_sidebar_error.png')
                raise e

            print("\n🛑 TEST: Mobile Bottom Tab Bar & Top Bar")
            mobile_page.goto(f'{BASE_URL}/portfolio')
            mobile_page.wait_for_load_state('domcontentloaded')
            
            try:
                # Top bar text on portfolio page is 'Portfolio' not 'Marffet'.
                # But to be safe across i18n, we check the nav fixed container.
                top_bar = mobile_page.locator("div.fixed.top-0.lg\\:hidden")
                top_bar.wait_for(state="visible", timeout=5000)
                print("✅ Mobile Top Bar found.")
                
                # Bottom tabs (use link hrefs instead of text because of i18n, filter for visible)
                mobile_page.locator('a[href="/mars"]').locator('visible=true').first.wait_for(state="visible", timeout=5000)
                mobile_page.locator('a[href="/portfolio"]').locator('visible=true').first.wait_for(state="visible", timeout=5000)
                print("✅ Bottom Tab Bar found.")
                
                mobile_page.screenshot(path=f'{SCREENSHOT_DIR}/mobile_tabs_ok.png')
            except Exception as e:
                print("❌ Mobile Top/Bottom bar missing!")
                mobile_page.screenshot(path=f'{SCREENSHOT_DIR}/mobile_tabs_error.png')
                raise e

        except Exception as e:
            print(f"💥 Error: {e}")
        finally:
            browser.close()
            print("🏁 Phase 31 UI Tests Complete")

if __name__ == "__main__":
    run_phase31_tests()
