import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
import os

def check_6669_2019():
    print("--- 6669 2019 Detail Check ---")
    
    # 1. Price
    fname = "data/raw/Market_2019_Prices.json"
    if os.path.exists(fname):
        with open(fname, 'r') as f:
            d = json.load(f)
            if '6669' in d:
                print(f"6669 Price Data: {d['6669']}")
            else:
                print("6669 Not Found in Price Cache")
    else:
        print("Price Cache Missing")

    # 2. Dividend
    fname = "data/raw/TWT49U_2019.json"
    if os.path.exists(fname):
        with open(fname, 'r') as f:
            d = json.load(f)
            rows = d.get('data', [])
            found = False
            for r in rows:
                if '6669' in str(r):
                    print(f"6669 Dividend Data: {r}")
                    found = True
            if not found:
                print("6669 Not Found in Dividend Cache")
    else:
        print("Dividend Cache Missing")

if __name__ == "__main__":
    check_6669_2019()
