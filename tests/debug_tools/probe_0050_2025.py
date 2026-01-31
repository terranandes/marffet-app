import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import requests

def probe():
    date_str = "20251210" # Today according to metadata, or yesterday if time diff
    # Usually data is available after 14:00
    url = "https://www.twse.com.tw/exchangeReport/MI_INDEX"
    params = {"response": "json", "date": date_str, "type": "ALLBUT0999"}
    
    print(f"Fetching {date_str}...")
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data['stat'] != 'OK':
            print(f"Stat: {data['stat']}")
            # Try previous day if today is empty (market invalid or weekend?)
            # But assume expected success for now.
            return

        tables = data.get('tables', [])
        found = False
        for i, t in enumerate(tables):
            # Check for 0050 in data
            rows = t.get('data', [])
            fields = t.get('fields', [])
            
            for r in rows:
                if r[0] == "0050" or r[0] == "2330":
                    print(f"Found {r[0]} in Table {i}: {t.get('title')}")
                    print(f"Fields: {fields}")
                    print(f"Row: {r}")
                    found = True
                    # Print index 8 value
                    if len(r) > 8:
                        print(f"Index 8 (Candidate) for {r[0]}: {r[8]}")
        
        if not found:
             print("0050 NOT FOUND in any table.")
             # Check if data9/data8 has it (legacy)
             d9 = data.get('data9', [])
             for r in d9:
                 if r[0] == "0050":
                     print("Found 0050 in data9")
                     print(f"Row: {r}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    probe()
