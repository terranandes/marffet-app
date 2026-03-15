import asyncio
import os
import sys
import argparse
from playwright.async_api import async_playwright
import time
import re

# Add project root to sys.path
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

ROUND = "round7"
EVIDENCE_DIR = os.path.join(BASE_DIR, "tests", "evidence", ROUND)

class Round7Tester:
    def __init__(self, target_url, viewport, is_mobile=False, session_cookie=None):
        self.target_url = target_url.rstrip("/")
        self.viewport = viewport
        self.is_mobile = is_mobile
        self.session_cookie = session_cookie
        self.evidence_path = EVIDENCE_DIR
        os.makedirs(self.evidence_path, exist_ok=True)
        self.account_name = "guest"
        self.prefix = ""

    def get_path(self, name):
        return os.path.join(self.evidence_path, f"{self.prefix}_{name}.png")

    async def login(self, page, context, email=None):
        if email and self.session_cookie:
            # Cookie injection mode (for remote Zeabur where TESTING=true is unavailable)
            self.account_name = email.split("@")[0]
            print(f"   [Auth] Injecting session cookie for {email}...")
            # Parse the target URL to extract domain
            from urllib.parse import urlparse
            parsed = urlparse(self.target_url)
            cookie_domain = parsed.hostname  # e.g. "marffet-app.zeabur.app"
            
            await context.add_cookies([{
                "name": "session",
                "value": self.session_cookie,
                "domain": cookie_domain,
                "path": "/",
                "httpOnly": True,
                "secure": parsed.scheme == "https",
                "sameSite": "Lax",
            }])
            # Navigate to portfolio to confirm session is active
            await page.goto(f"{self.target_url}/portfolio", wait_until="networkidle")
            await asyncio.sleep(2)
            print(f"   [Auth] Cookie injected, navigated to /portfolio")
        elif email:
            # Mock login mode (local with TESTING=true)
            self.account_name = email.split("@")[0]
            print(f"   [Auth] Logging in as {email} via test-login...")
            await page.goto(f"{self.target_url}/auth/test-login?email={email}", wait_until="networkidle")
            await page.goto(f"{self.target_url}/portfolio", wait_until="networkidle")
        else:
            self.account_name = "guest"
            print(f"   [Auth] Entering as Guest...")
            await page.goto(f"{self.target_url}/portfolio", wait_until="domcontentloaded")
            await asyncio.sleep(2)
            guest_btn = page.locator('button', has_text=re.compile(r"Explore as Guest|以訪客身分探索", re.I))
            if await guest_btn.count() > 0 and await guest_btn.first.is_visible():
                await guest_btn.first.click()
                await asyncio.sleep(1)
        
        self.prefix = f"{ROUND}_{self.account_name}_{'mobile' if self.is_mobile else 'desktop'}"

    async def verify_area_a(self, page):
        print(f"   [Area A] Navigation & Landing")
        await page.goto(f"{self.target_url}/", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        await page.screenshot(path=self.get_path("area_a_home"), full_page=True)
        if self.is_mobile:
            await page.screenshot(path=self.get_path("area_a_mobile_tabs"))
        else:
            await page.screenshot(path=self.get_path("area_a_sidebar"))

    async def verify_area_b(self, page):
        print(f"   [Area B] Mars Strategy")
        await page.goto(f"{self.target_url}/mars", wait_until="networkidle")
        await asyncio.sleep(3)  # Allow table rendering
        # Wait for either table or card view
        try:
            await page.wait_for_selector("table, th, .glass-card, [class*='mars']", timeout=20000)
        except:
            print("   [Area B] Warning: Table header timeout, checking for data rows...")
        
        await page.screenshot(path=self.get_path("area_b_mars_table"), full_page=True)
        
        # Click a row/card to show chart
        rows = page.locator("tr", has_text=re.compile(r'\d{4}'))
        if await rows.count() == 0:
             rows = page.locator("tbody tr")
        
        if await rows.count() > 0:
            target_row = rows.nth(0)
            await target_row.scroll_into_view_if_needed()
            await target_row.click()
            await asyncio.sleep(3)
            await page.screenshot(path=self.get_path("area_b_mars_chart"), full_page=True)
        else:
            print("   [Area B] Warning: No data rows found in Mars table.")
            await page.screenshot(path=self.get_path("area_b_mars_list"), full_page=True)

    async def verify_area_e(self, page):
        print(f"   [Area E] Portfolio CRUD")
        await page.goto(f"{self.target_url}/portfolio", wait_until="networkidle")
        await asyncio.sleep(3)
        
        # Explicitly wait for portfolio data to load
        try:
            await page.wait_for_selector(".glass-card, button[role='tab'], [class*='portfolio'], [class*='group']", timeout=15000)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"   [Area E] Warning: Timeout waiting for portfolio data elements: {e}")
            
        await page.screenshot(path=self.get_path("area_e_portfolio_main"), full_page=True)
        await page.screenshot(path=self.get_path("area_e_portfolio_refresh"))

    async def verify_area_i(self, page):
        print(f"   [Area I] AI Copilot")
        await page.goto(f"{self.target_url}/portfolio", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        fab = page.locator("button", has_text=re.compile(r"✨"))
        if await fab.count() > 0:
            await fab.first.click()
            await asyncio.sleep(1)
            await page.screenshot(path=self.get_path("area_i_ai_sidebar"))

    async def run_full_pass(self, email=None):
        async with async_playwright() as p:
            vp_label = "Mobile" if self.is_mobile else "Desktop"
            print(f"🚀 Starting verification for {email or 'Guest'} ({vp_label})")
            browser = await p.chromium.launch(headless=True)
            context_args = {"viewport": self.viewport}
            if self.is_mobile:
                context_args.update(p.devices["iPhone 12"])
            
            context = await browser.new_context(**context_args)
            page = await context.new_page()
            
            try:
                await self.login(page, context, email)
                await self.verify_area_a(page)
                await self.verify_area_b(page)
                await self.verify_area_e(page)
                await self.verify_area_i(page)
                # Area J for admin if email is terranfund
                if email == "terranfund@gmail.com":
                    print(f"   [Area J] Admin Dashboard")
                    await page.goto(f"{self.target_url}/admin", wait_until="domcontentloaded")
                    await asyncio.sleep(2)
                    await page.screenshot(path=self.get_path("area_j_admin"), full_page=True)
                
                print(f"✅ Pass complete for {email or 'Guest'}")
            except Exception as e:
                print(f"❌ Error during pass: {e}")
                import traceback
                traceback.print_exc()
                await page.screenshot(path=self.get_path("error"))
            finally:
                await browser.close()

async def main():
    parser = argparse.ArgumentParser(description="Round 7 Full Feature Verification Suite")
    parser.add_argument("--target", choices=["local", "remote"], default="local",
                        help="Target environment: local (localhost:3000) or remote (Zeabur)")
    parser.add_argument("--session-cookie", type=str, default=None,
                        help="Session cookie value to inject (for remote non-guest auth)")
    parser.add_argument("--email", type=str, default=None,
                        help="Single email to test (when used with --session-cookie)")
    args = parser.parse_args()
    
    target_url = "http://localhost:3000" if args.target == "local" else "https://marffet-app.zeabur.app"
    
    desktop_vp = {"width": 1280, "height": 800}
    mobile_vp = {"width": 390, "height": 844}
    
    if args.session_cookie and args.email:
        # Cookie injection mode: run only for the specified email
        for is_mobile, vp in [(False, desktop_vp), (True, mobile_vp)]:
            tester = Round7Tester(target_url, vp, is_mobile=is_mobile, session_cookie=args.session_cookie)
            await tester.run_full_pass(args.email)
    elif args.session_cookie:
        print("ERROR: --session-cookie requires --email to be specified.")
        sys.exit(1)
    else:
        # Standard mode: run all accounts
        accounts = [None, "terranfund@gmail.com", "terranstock@gmail.com"]
        for email in accounts:
            for is_mobile, vp in [(False, desktop_vp), (True, mobile_vp)]:
                tester = Round7Tester(target_url, vp, is_mobile=is_mobile)
                await tester.run_full_pass(email)

if __name__ == "__main__":
    asyncio.run(main())
