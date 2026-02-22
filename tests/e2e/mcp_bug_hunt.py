import json
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = Path("tests/evidence")
JIRA_DIR = Path("docs/jira")

EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
JIRA_DIR.mkdir(parents=True, exist_ok=True)

def file_bug(bug_id: int, desc: str, screenshot_path: str):
    slug = desc.lower().replace(" ", "_").replace("/", "_")
    bug_file = JIRA_DIR / f"BUG-{bug_id}-CV_{slug}.md"
    content = f"""# BUG-{bug_id}
**Reporter:** [CV]
**Type:** Regression / Functional Bug
**Description:** {desc}
**Evidence:** {screenshot_path}
"""
    with open(bug_file, "w") as f:
        f.write(content)
    print(f"Filed Bug: {bug_file}")

def run_local_tests():
    print("Starting Playwright Local Verification...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        base_url = "http://localhost:3000"
        ts = int(time.time())
        
        try:
            # 1. Mars Strategy Rendering
            page.goto(f"{base_url}/mars")
            page.wait_for_load_state('networkidle')
            time.sleep(2)  # Allow APIs to populate tables
            
            rows = page.locator("table tbody tr").count()
            print(f"Mars Strategy Rows: {rows}")
            
            if rows == 0:
                ss_path = EVIDENCE_DIR / f"bug_{ts}_mars_strategy_empty.png"
                page.screenshot(path=str(ss_path), full_page=True)
                file_bug(112, "Mars Strategy Shows 0 Results", str(ss_path))
            
            # 2. Bar Chart Race Rendering
            page.goto(f"{base_url}/race")
            page.wait_for_load_state('domcontentloaded')
            time.sleep(2)
            
            print(f"{base_url} Verification Completed.")
        except Exception as e:
            ss_path = EVIDENCE_DIR / f"bug_{ts}_{base_url.replace('://', '_').replace('/', '_')}_crash.png"
            page.screenshot(path=str(ss_path), full_page=True)
            file_bug(999, f"Playwright Execution Crash on {base_url}: {str(e)[:50]}", str(ss_path))
            print(f"Failed: {e}")
        finally:
            browser.close()

def run_remote_tests():
    print("Starting Playwright Remote Verification...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        base_url = "https://martian-app.zeabur.app"
        ts = int(time.time())
        
        try:
            # 1. Mars Strategy Rendering
            page.goto(f"{base_url}/mars")
            page.wait_for_load_state('networkidle')
            time.sleep(3)  # Allow APIs to slow-start on remote
            
            rows = page.locator("table tbody tr").count()
            print(f"Remote Mars Strategy Rows: {rows}")
            
            if rows == 0:
                ss_path = EVIDENCE_DIR / f"bug_{ts}_remote_mars_strategy_empty.png"
                page.screenshot(path=str(ss_path), full_page=True)
                file_bug(113, "Remote Zeabur Mars Strategy Shows 0 Results", str(ss_path))
                
            # 2. Bar Chart Race Rendering
            page.goto(f"{base_url}/race")
            page.wait_for_load_state('domcontentloaded')
            time.sleep(2)
            
            print(f"{base_url} Verification Completed.")
        except Exception as e:
            ss_path = EVIDENCE_DIR / f"bug_{ts}_remote_crash.png"
            page.screenshot(path=str(ss_path), full_page=True)
            file_bug(998, f"Remote Playwright Execution Crash: {str(e)[:50]}", str(ss_path))
            print(f"Failed: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run_local_tests()
    # Note: run_remote_tests is explicitly called downstream after deploy
