
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        print("Navigating to Login (Dev Mode)...")
        # Use the dev_login endpoint to set session cookie
        await page.goto("http://localhost:3000/auth/dev/login")
        
        # Wait for Portfolio to load (look for "Portfolio" in the sidebar or main area)
        # The new UI shows "Mars Strategy System" on home, but sidebar has "Portfolio"
        print("Waiting for Dashboard...")
        await page.wait_for_selector("text=Mars Strategy System", timeout=10000)
        
        # Debug Cookies
        cookies = await context.cookies()
        print(f"DEBUG: Cookies after login: {cookies}")
        
        print("✅ Login Successful (Admin Session Set).")
        await page.screenshot(path="tests/screenshots/login_success.png")

        # 2. Check Trend Page
        print("Checking Trend Page...")
        await page.click("text=Trend")
        await page.wait_for_timeout(2000) # Wait for chart
        trend_content = await page.content()
        if "No Transaction History" not in trend_content:
            print("✅ Trend Page Loaded Data.")
        else:
            print("❌ Trend Page Empty.")
        await page.screenshot(path="tests/screenshots/trend_page.png")

        # 3. Check AI Copilot
        print("Checking AI Copilot...")
        # Reload to ensure context is injected
        await page.reload()
        await page.wait_for_timeout(2000)
        
        # Click FAB
        fab = page.locator("button[title='Open AI Copilot']")
        if await fab.count() > 0:
            await fab.click()
            await page.wait_for_timeout(1000)
            
            # Send Message
            await page.get_by_placeholder("Ask Mars AI...").fill("Can you see my portfolio?")
            await page.get_by_role("button", name="➤").click()
            
            # Wait for response
            await page.wait_for_timeout(5000)
            ai_response = await page.locator(".bg-zinc-700").last.text_content()
            print(f"AI Response: {ai_response}")
            
            if "DATA VOID" not in ai_response and "portfolio" in ai_response.lower():
                 print("✅ AI Copilot Context Working.")
            else:
                 print("⚠️ AI Copilot Response inconclusive.")
            await page.screenshot(path="tests/screenshots/ai_chat.png")
        else:
            print("❌ AI Copilot FAB not found.")

        # 4. Check Admin Dashboard
        print("Checking Admin Dashboard...")
        await page.goto("http://localhost:3000/admin")
        await page.wait_for_selector("text=GM Dashboard", timeout=5000)
        print("✅ Admin Dashboard Loaded.")
        await page.screenshot(path="tests/screenshots/admin_page.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
