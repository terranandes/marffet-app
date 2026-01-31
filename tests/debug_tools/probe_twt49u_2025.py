import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import requests

def probe_dividend():
    # TWT49U: Stock Dividend and Capital Increase
    url = "https://www.twse.com.tw/exchangeReport/TWT49U"
    # Fetch whole year 2025
    params = {
        "response": "json",
        "strDate": "20250101",
        "endDate": "20251231"
    }
    
    print("Fetching TWT49U for 2025...")
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data['stat'] != 'OK':
            print(f"Stat: {data['stat']}")
            return

        rows = data.get('data', [])
        found = False
        print(f"Total Rows: {len(rows)}")
        
        for r in rows:
            # Fields usually: Date, Code, Name, Before, After, ...
            # Let's print rows for 0050
            if r[1] == "0050":
                print(f"Found 0050 Dividend/Split: {r}")
                found = True
        
        if not found:
            print("No TWT49U record found for 0050 in 2025.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    probe_dividend()
