
import asyncio
import argparse
import json
import os
import sys
import time
import re
from playwright.sync_api import sync_playwright

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

DATA_DIR = "data/raw_dividends"
REF_FILE = "data/ref/stock_par_values.json"

def get_ky_dr_stocks(start_year=2024, end_year=2024):
    """Scan TWT49U cache for KY/DR stocks."""
    targets = {}
    print(f"🔍 Scanning TWT49U cache for KY/DR stocks...")
    
    # We only need one recent year to get the bulk of active stocks
    # But checking a few years helps if they didn't pay dividends recently
    for year in range(2020, 2026):
        cache_file = os.path.join(DATA_DIR, f"TWSE_Dividends_{year}.json")
        if not os.path.exists(cache_file):
            continue
            
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                
            for stock_id, info in data.items():
                name = info.get('name', '')
                # Filter for KY or DR or * (which often implies special status)
                if 'KY' in name or 'DR' in name or '*' in name:
                    targets[stock_id] = name
        except Exception as e:
            print(f"  ❌ Error reading {cache_file}: {e}")
            
    print(f"✅ Found {len(targets)} unique KY/DR/* stocks.")
    return targets

def parse_stock_meta(page, stock_id):
    """Parse Goodinfo Basic Info for Par Value."""
    # Usage: StockDetail.asp?STOCK_ID=4763
    url = f"https://goodinfo.tw/tw/StockDetail.asp?STOCK_ID={stock_id}"
    # print(f"  globe Fetching {stock_id}...")
    
    try:
        page.goto(url, timeout=45000, wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass # Networkidle might timeout if ads are loading, proceed anyway
            
        time.sleep(2) # Polite delay + extensive robust wait
        
        # Retry loop for content
        content = ""
        for _ in range(3):
            try:
                content = page.content()
                if "每股面額" in content:
                    break
            except Exception as e:
                print(f"    Retrying content fetch... ({e})")
                time.sleep(1)

        
        # Regex search in full HTML (faster/more robust than complex selectors given Goodinfo's tables)
        # Pattern: 每股面額.*?([\d\.]+)\s*元
        # But sometimes it's "10 元" or "USD 5"
        
        # Check specific row in Basic Info
        # Usually row: 產業別 ... 每股面額 ...
        
        # Let's use robust scraping:
        # Find cell with "每股面額"
        
        # locator = page.locator("td:has-text('每股面額')")
        # count = locator.count()
        # if count > 0:
        #     # Get text of NEXT cell? or parent row?
        #     # Often: <td>每股面額</td><td>10元</td>
        #     target_cell = locator.first.locator("+ td")
        #     text = target_cell.inner_text().strip()
        #     return text
        
        # Regex fallback is often safest for "Property: Value" pairs
        # Pattern matches: "每股面額</td><td bgcolor='white'>10元</td>"
        # Or text-based regex
        
        match = re.search(r'每股面額.*?<td[^>]*>(.*?)</td>', content, re.DOTALL)
        if match:
            raw = match.group(1).strip()
            clean = re.sub('<[^>]+>', '', raw).strip()
            return clean
            
        # Fallback: Search visible text
        body_text = page.inner_text("body")
        match_text = re.search(r'每股面額\s+(.+?)(\n|$)', body_text)
        if match_text:
            return match_text.group(1).strip()

        # Debug Screenshot if not found
        # print(f"    Scanning page content failed. Taking debug screenshot...")
        os.makedirs("data/ref/debug", exist_ok=True)
        page.screenshot(path=f"data/ref/debug/debug_{stock_id}.jpg")
        # print(f"    Saved debug screenshot to data/ref/debug/debug_{stock_id}.jpg")

        return None

    except Exception as e:
        print(f"  ❌ Error processing {stock_id}: {e}")
        return None

def normalize_par_value(par_str):
    """Convert '10元', '5美元', etc. to TWD equivalent or raw number."""
    if not par_str: return 10.0 # Default
    
    # Common formats:
    # "新台幣 10 元"
    # "10元"
    # "美金 0.5 元"
    # "無面額"
    
    try:
        # Remove commas
        s = par_str.replace(',', '')
        
        # Detect currency
        currency = 'TWD'
        if '美' in s or 'USD' in s: currency = 'USD'
        if '民' in s or 'RMB' in s: currency = 'RMB'
        if '無' in s: return 10.0 # Treat as standard for now? Or 0?
        
        # Extract number
        nums = re.findall(r'[\d\.]+', s)
        if not nums: return 10.0
        
        val = float(nums[0])
        
        # We need to return the PAR VALUE that aligns with TWT49U.
        # However, TWT49U might report TWD value or Raw Value.
        # Let's just store the parsed value and currency for now.
        # The normalization logic will happen in the crawler/calculator.
        
        return {
            'value': val,
            'currency': currency,
            'raw': par_str
        }
    except:
        return {'value': 10.0, 'currency': 'TWD', 'raw': par_str}

def main():
    parser = argparse.ArgumentParser(description="Fetch Stock Par Values")
    parser.add_argument("--all", action="store_true", help="Fetch ALL stocks (not just KY/DR)")
    parser.add_argument("--targets", type=str, help="Comma-separated list")
    args = parser.parse_args()

    # 1. Load existing
    if os.path.exists(REF_FILE):
        with open(REF_FILE, 'r') as f:
            ref_data = json.load(f)
    else:
        ref_data = {}

    # 2. Identify targets
    if args.targets:
        targets = {t: 'Target' for t in args.targets.split(',')}
    elif args.all:
        # TODO: Implement all scan
        targets = get_ky_dr_stocks() # Placeholder
    else:
        targets = get_ky_dr_stocks()
        
    # Filter out already done?
    # todo_ids = [s for s in targets if s not in ref_data]
    todo_ids = sorted(list(targets.keys()))
    
    print(f"🚀 Starting fetch for {len(todo_ids)} stocks...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        dirty = False
        
        for i, stock_id in enumerate(todo_ids):
            # Skip if already has valid data (optional, for speed)
            if stock_id in ref_data and 'par_value' in ref_data[stock_id]:
                 continue

            print(f"[{i+1}/{len(todo_ids)}] {stock_id} {targets[stock_id]}...")
            
            raw_par = parse_stock_meta(page, stock_id)
            
            if raw_par:
                parsed = normalize_par_value(raw_par)
                ref_data[stock_id] = {
                    'name': targets[stock_id],
                    'par_raw': raw_par, # Keep raw string
                    'par_val': parsed['value'],
                    'par_curr': parsed['currency'],
                    'updated': datetime.now().isoformat()
                }
                print(f"  ✅ Par: {raw_par} -> {parsed['value']} {parsed['currency']}")
                dirty = True
            else:
                print(f"  ⚠️  No Par Value found")
            
            if i % 10 == 0 and dirty:
                with open(REF_FILE, 'w') as f:
                    json.dump(ref_data, f, indent=2, sort_keys=True)
                dirty = False
                
        browser.close()
        
    with open(REF_FILE, 'w') as f:
        json.dump(ref_data, f, indent=2, sort_keys=True)
    print(f"💾 Saved metadata to {REF_FILE}")

if __name__ == "__main__":
    from datetime import datetime
    main()
