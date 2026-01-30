
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to http://localhost:3000...")
        await page.goto("http://localhost:3000")
        await page.wait_for_timeout(5000)
        
        print("Page Content:")
        print(await page.content())
        
        await page.screenshot(path="tests/screenshots/debug_login.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
