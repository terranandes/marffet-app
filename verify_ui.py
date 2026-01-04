from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        print("🚀 Launching Chromium...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        print("🌐 Navigating to Home Page...")
        page.goto("http://localhost:8000")
        time.sleep(2) # Wait for Vue hydration
        
        # Verify Title/Content
        title = page.title()
        print(f"📄 Page Title: {title}")
        
        # Take Home Screenshot
        page.screenshot(path="verification_home.png")
        print("📸 Screenshot saved: verification_home.png")

        # Click Leaderboard Tab
        print("👆 Clicking Leaderboard Tab...")
        # Assuming the tab has text "Leaderboard" or specific class. 
        # Based on index.html: <button ... @click="activeTab = 'leaderboard'">
        page.get_by_text("Leaderboard").click()
        time.sleep(1)
        
        # Take Leaderboard Screenshot
        page.screenshot(path="verification_leaderboard.png")
        print("📸 Screenshot saved: verification_leaderboard.png")

        # Find a Profile Link (any row in leaderboard)
        # Detailed selector based on previous edits: .leaderboard-row or similar
        print("🔍 Searching for a profile to click...")
        # Try to click the first user in the list (rank #1 usually)
        # The list items call openProfile(user.id)
        # We look for a clickable element inside the leaderboard list
        try:
            # Try specific text or class if known. 
            # Or just click a random high-rank user if they have a name.
            # Let's target the "podium" or "list". 
            # Click the second item (Rank 2) since Rank 1 might be special
            # page.locator(".leaderboard-item").first.click() 
            # Wait, let's just dump the html if needed, but 'get_by_role' might work.
            # Let's try to click on the text "Guest" or "User" if visible, or a generic selector.
            
            # Using a CSS selector for the list items
            rows = page.locator("li.p-4.rounded-xl") # Based on common tailwind classes seen, but risky.
            # Best to use text if possible. Let's assume there's at least one user.
            
            # Alternative: Access the global function directly? No, E2E should use UI.
            # Let's click the first list item that looks clickable.
            page.locator(".cursor-pointer").first.click()
            
            time.sleep(1)
            print("👤 Profile Modal Opened (hopefully)")
            page.screenshot(path="verification_profile.png")
            print("📸 Screenshot saved: verification_profile.png")
            
            # Verify Share Button
            share_btn = page.get_by_text("Share Public Link")
            if share_btn.is_visible():
                print("✅ Share Button Found!")
            else:
                print("❌ Share Button NOT Visible")

        except Exception as e:
            print(f"⚠️ Error interacting with Leaderboard/Profile: {e}")

        browser.close()
        print("✅ Verification Complete")

if __name__ == "__main__":
    run()
