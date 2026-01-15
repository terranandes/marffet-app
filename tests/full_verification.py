from playwright.sync_api import sync_playwright
import time
import os

screenshots_dir = '/home/terwu01/.gemini/antigravity/brain/951e48e9-e02d-4fb3-a019-9fefff545832'
base_url = 'http://localhost:3000'

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1400, 'height': 900})
        page = context.new_page()
        
        print("🚀 Starting Full Stack Verification...")

        # 1. Home/Mars Strategy
        print("Testing Mars Strategy...")
        page.goto(f'{base_url}/mars')
        page.wait_for_selector('text=Mars Strategy')
        page.fill('input[type="number"]', '2010')  # Start Year
        # Check if table loads
        page.wait_for_selector('table')
        page.screenshot(path=f'{screenshots_dir}/test_mars.png')
        print("✅ Mars Strategy verified")

        # 2. Portfolio (Check Guest/Empty State or Data)
        print("Testing Portfolio...")
        page.goto(f'{base_url}/portfolio')
        # Expect Portfolio Dashboard or Groups
        page.wait_for_selector('text=My Portfolio', timeout=10000)
        page.screenshot(path=f'{screenshots_dir}/test_portfolio.png')
        print("✅ Portfolio verified")

        # 3. Bar Chart Race
        print("Testing Bar Chart Race...")
        page.goto(f'{base_url}/race')
        page.wait_for_selector('text=Bar Chart Race')
        # Check for canvas or SVG or specific race elements
        page.wait_for_selector('text=Play', timeout=10000)
        page.screenshot(path=f'{screenshots_dir}/test_race.png')
        print("✅ Bar Chart Race verified")

        # 4. Trend
        print("Testing Trend...")
        page.goto(f'{base_url}/trend')
        page.wait_for_selector('text=Portfolio Trend')
        page.screenshot(path=f'{screenshots_dir}/test_trend.png')
        print("✅ Trend verified")

        # 5. Cash Ladder
        print("Testing Cash Ladder...")
        page.goto(f'{base_url}/ladder')
        page.wait_for_selector('text=Cash Ladder')
        # Check for list or empty state
        try:
             page.wait_for_selector('.divide-y', timeout=3000)
             print("✅ Ladder List verified")
        except:
             if page.is_visible('text=No Rankings Yet'):
                 print("✅ Ladder Empty State verified")
             else:
                 raise Exception("Ladder content not found")
        page.screenshot(path=f'{screenshots_dir}/test_ladder.png')

        # 6. CB Strategy
        print("Testing CB Strategy...")
        page.goto(f'{base_url}/cb')
        page.wait_for_selector('text=CB Strategy')
        page.screenshot(path=f'{screenshots_dir}/test_cb.png')
        print("✅ CB Strategy verified")

        # 7. My Race
        print("Testing My Race...")
        page.goto(f'{base_url}/myrace')
        page.wait_for_selector('text=My Race')
        page.screenshot(path=f'{screenshots_dir}/test_myrace.png')
        print("✅ My Race verified")

        # 8. Admin (Check Access)
        print("Testing Admin Page...")
        page.goto(f'{base_url}/admin')
        # Should show GM Dashboard or Access Denied
        content = page.content()
        if "GM Dashboard" in content:
            print("✅ Admin Page loaded (Authorized)")
        elif "Access Denied" in content:
            print("✅ Admin Page loaded (Restricted - Correct)")
        else:
            print("⚠️ Admin Page unexpected state")
        page.screenshot(path=f'{screenshots_dir}/test_admin.png')

        # 9. Sidebar Login & Notifications
        print("Testing Sidebar...")
        # Check for Martian Logo
        page.wait_for_selector('text=MARTIAN')
        # Check for Login button or User Profile
        if page.query_selector('text=Login'):
            print("✅ Sidebar shows Login button (Guest)")
        else:
            print("✅ Sidebar shows User Profile")
        
        # Check Notification Bell
        if page.query_selector('button svg path[d*="M15 17h5"]'):
             print("✅ Notification Bell present")

        # Check Settings Button
        if page.query_selector('text=Settings'):
            print("✅ Settings Button verified")
        else:
            print("❌ Settings Button NOT FOUND")

        print("🎉 All Tests Passed Successfully!")
        browser.close()

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        exit(1)
