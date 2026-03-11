import asyncio
from playwright.async_api import async_playwright
import os
import shutil
import time

EVIDENCE_DIR = "tests/evidence/round3"

async def test_auth_flow(page, context, index, email):
    print(f"\n--- Testing Account: {email} ---")
    
    # Go to app
    await page.goto("http://localhost:3000", timeout=45000, wait_until="domcontentloaded")
    
    # 1. Login
    print(f"[{index}] Logging in as {email}...")
    login_res = await context.request.post(f"http://localhost:8000/auth/guest?email={email}")
    if not login_res.ok:
        print(f"[{index}] Warning: Login returned status {login_res.status}")
        
    await page.goto("http://localhost:3000/")
    
    # Wait for dashboard items to load to confirm login
    try:
        await page.wait_for_selector(".grid", timeout=15000)
    except Exception:
        pass
    try:
        await page.wait_for_selector("button[title='Settings']", timeout=20000)
    except Exception:
        # If mobile layout or not found, try something else
        pass
        
    time.sleep(2)  # Let animations settle
    
    # Take screenshot of Dashboard
    await page.screenshot(path=f"{EVIDENCE_DIR}/{index}a_{email.split('@')[0]}_dashboard.png", full_page=True)
    
    # 2. Check Settings
    print(f"[{index}] Checking Settings representation...")
    try:
        settings_btn = page.locator("button[title='Settings']").first
        await settings_btn.click(force=True)
        # Give modal a moment to animate in
        time.sleep(2)
        
        # Take screenshot of whatever is currently shown in settings
        await page.screenshot(path=f"{EVIDENCE_DIR}/{index}b_{email.split('@')[0]}_settings.png")
        
        # Wait for the logout button (red text) to appear inside the modal
        await page.wait_for_selector("button.text-red-500", timeout=5000)
        
        # 3. Logout
        print(f"[{index}] Logging out via settings...")
        logout_btn = page.locator("button.text-red-500").first
        await logout_btn.click(force=True)
        
        # Wait for redirect to public/auth block view
        await page.wait_for_selector("button:has-text('Sign In'), button:has-text('登入')", timeout=15000)
        await page.screenshot(path=f"{EVIDENCE_DIR}/{index}c_{email.split('@')[0]}_logged_out.png", full_page=True)
        print(f"[{index}] ✅ Flow complete for {email}")
    except Exception as e:
        print(f"[{index}] ❌ Failed during settings/logout: {e}")
        try:
            html = await page.content()
            with open(f"{EVIDENCE_DIR}/{index}_error.html", "w") as f:
                f.write(html)
        except Exception:
            pass

    # Do not clear cookies here; let the flow be continuous
    
async def run():
    print("=== Phase 35: Round 3 Sequential Login Verification ===")
    if os.path.exists(EVIDENCE_DIR):
        shutil.rmtree(EVIDENCE_DIR)
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Desktop context
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            device_scale_factor=2
        )
        page = await context.new_page()
        
        # Sequential Flow: A -> B -> A
        accounts_flow = ["terranstock@gmail.com", "terranandes@gmail.com", "terranstock@gmail.com"]
        for i, email in enumerate(accounts_flow):
            await test_auth_flow(page, context, i+1, email)
            
        await browser.close()
    print(f"\\n✅ Round 3 Complete! Evidence saved in {EVIDENCE_DIR}/")

if __name__ == "__main__":
    asyncio.run(run())
