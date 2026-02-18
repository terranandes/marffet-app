
import requests
import time
import json
import os
import argparse
import re
from bs4 import BeautifulSoup
from datetime import datetime

REF_FILE = "data/ref/stock_par_values_mops.json"

def fetch_mops_basic_info(co_id):
    """Fetch Basic Info from MOPS (t05st03)."""
    url = "https://mops.twse.com.tw/mops/web/ajax_t05st03"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://mops.twse.com.tw',
        'Referer': 'https://mops.twse.com.tw/mops/web/t05st03'
    }
    
    data = {
        'encodeURIComponent': '1',
        'step': '1',
        'firstin': '1',
        'off': '1',
        'keyword4': '',
        'code1': '',
        'TYPEK2': '',
        'checkbtn': '',
        'queryName': 'co_id',
        'inpuType': 'co_id',
        'co_id': co_id
    }
    
    try:
        r = requests.post(url, data=data, headers=headers, timeout=15)
        r.encoding = 'utf-8'
        
        if "THE PAGE CANNOT BE ACCESSED" in r.text:
            print(f"  ❌ MOPS Blocked Request for {co_id}")
            return None
            
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Look for "每股面額" in table cells
        # Usually in a table with class 'hasBorder'
        
        # Search all 'th' or 'td' with text '每股面額'
        target_th = soup.find(lambda tag: tag.name in ['th', 'td'] and "每股面額" in tag.text)
        
        if target_th:
            # The value is usually in the NEXT sibling td
            val_td = target_th.find_next_sibling('td')
            if val_td:
                raw_text = val_td.text.strip()
                return raw_text
                
        # Regex fallback on full text
        text = soup.get_text()
        match = re.search(r'每股面額[:：]?\s*([^\n\r]+)', text)
        if match:
            return match.group(1).strip()
            
        return None

    except Exception as e:
        print(f"  ❌ Error fetching MOPS {co_id}: {e}")
        return None

def normalize_par(par_str):
    if not par_str: return 10.0
    try:
        # Expected: "新台幣 10.0000元" or "美金 0.5000元"
        s = par_str.replace(',', '')
        currency = 'TWD'
        if '美' in s or 'USD' in s: currency = 'USD'
        if '民' in s or 'RMB' in s: currency = 'RMB'
        if '無' in s: return {'value': 10.0, 'currency': 'TWD', 'raw': par_str} # Treat as standard?
        
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
    
    targets = args.targets.split(',') if args.targets else []
    if not targets:
        print("Please provide --targets")
        return

    results = {}
    if os.path.exists(REF_FILE):
        with open(REF_FILE, 'r') as f:
            results = json.load(f)

    for code in targets:
        print(f"Fetching {code} from MOPS...")
        raw = fetch_mops_basic_info(code)
        if raw:
            parsed = normalize_par(raw)
            print(f"  ✅ Par: {parsed['raw']} -> {parsed['value']} {parsed['currency']}")
            results[code] = parsed
        else:
            print(f"  ⚠️  Par Value not found for {code}")
        
        time.sleep(3) # Polite

    with open(REF_FILE, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Saved to {REF_FILE}")

if __name__ == "__main__":
    main()
