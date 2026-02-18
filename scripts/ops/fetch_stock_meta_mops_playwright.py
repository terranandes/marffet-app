
import argparse
import json
import os
import re
import time
from playwright.sync_api import sync_playwright

REF_FILE = "data/ref/stock_par_values_mops.json"

def fetch_par_value(page, code):
    """Fetch Par Value from MOPS t05st03 using Playwright."""
    url = "https://mops.twse.com.tw/mops/web/t05st03"
    
    try:
        # Navigate
        page.goto(url, timeout=30000)
        
        # Determine if listed (SII), OTC, or Emerging
        # Actually MOPS search usually handles it, but we need to select "公司代號" input
        
        # Wait for input
        page.wait_for_selector("input#co_id")
        
        # Fill code
        page.fill("input#co_id", code)
        
        # Click Search (button might be different depending on layout, usually "查詢")
        # Selector often: input[type='button'][value=' 查詢 ']
        page.click("input[type='button'][value=' 查詢 ']")
        
        # Wait for result table
        # Table usually has class 'hasBorder'
        page.wait_for_selector("table.hasBorder", timeout=10000)
        time.sleep(1) 
        
        # Get content
        content = page.content()
        
        # Parse for "每股面額"
        # Table row: <th>每股面額</th><td>新台幣 10.0000元</td>
        match = re.search(r'每股面額.*?<td[^>]*>(.*?)</td>', content, re.DOTALL)
        if match:
            raw = match.group(1).strip()
            # Clean tags
            clean = re.sub('<[^>]+>', '', raw).strip()
            return clean
            
        # Try finding by text if regex fails (sometimes th/td structure varies)
        # body_text = page.inner_text("body")
        # match_text = re.search(r'每股面額\s+(.+?)(\n|$)', body_text)
        # if match_text:
        #     return match_text.group(1).strip()
            
        return None
        
    except Exception as e:
        print(f"  ❌ Error fetching {code}: {e}")
        os.makedirs("data/ref/debug", exist_ok=True)
        page.screenshot(path=f"data/ref/debug/debug_mops_{code}.jpg")
        print(f"    Saved debug screenshot to data/ref/debug/debug_mops_{code}.jpg")
        return None

def normalize_par(par_str):
    if not par_str: return 10.0
    try:
        s = par_str.replace(',', '')
        currency = 'TWD'
        if '美' in s or 'USD' in s: currency = 'USD'
        if '民' in s or 'RMB' in s: currency = 'RMB'
        if '日' in s or 'JPY' in s: currency = 'JPY'
        if '無' in s: return {'value': 10.0, 'currency': 'TWD', 'raw': par_str}
        
        nums = re.findall(r'[\d\.]+', s)
        if nums:
            return {'value': float(nums[0]), 'currency': currency, 'raw': par_str}
        return {'value': 10.0, 'currency': 'TWD', 'raw': par_str}
    except:
        return {'value': 10.0, 'currency': 'TWD', 'raw': par_str}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", type=str, help="Comma-separated IDs")
    args = parser.parse_args()
    
    current_data = {}
    if os.path.exists(REF_FILE):
        with open(REF_FILE, 'r') as f:
            current_data = json.load(f)
            
    targets = args.targets.split(',') if args.targets else []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for code in targets:
            print(f"Fetching {code} from MOPS (Playwright)...")
            raw = fetch_par_value(page, code)
            
            if raw:
                parsed = normalize_par(raw)
                print(f"  ✅ Par: {parsed['raw']} -> {parsed['value']} {parsed['currency']}")
                current_data[code] = parsed
            else:
                print(f"  ⚠️  Par Value not found for {code}")
            
            time.sleep(2) # Polite
            
        browser.close()
        
    with open(REF_FILE, 'w') as f:
        json.dump(current_data, f, indent=2, ensure_ascii=False)
    print(f"Saved to {REF_FILE}")

if __name__ == "__main__":
    main()
