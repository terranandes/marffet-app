import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import requests

def probe_split_detail():
    # 1. TWT49U for 20250618
    url_div = "https://www.twse.com.tw/exchangeReport/TWT49U"
    params_div = {
        "response": "json",
        "strDate": "20250618",
        "endDate": "20250618"
    }
    print("Fetching TWT49U for 20250618...")
    try:
        resp = requests.get(url_div, params=params_div, timeout=10)
        data = resp.json()
        if data['stat'] == 'OK':
            rows = data.get('data', [])
            print(f"TWT49U Rows: {len(rows)}")
            for r in rows:
                print(f"Row: {r}")
        else:
            print(f"TWT49U Stat: {data['stat']}")
    except Exception as e:
        print(f"Error TWT49U: {e}")

    # 2. Prices - Disabled
    print("Prices Probe disabled.")

if __name__ == "__main__":
    probe_split_detail()
