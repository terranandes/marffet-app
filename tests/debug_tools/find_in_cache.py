import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
import os
import glob

target = "6664"
data_dir = "data/raw"

files = sorted(glob.glob(os.path.join(data_dir, "*_Market_*_Prices.json")))

print(f"Scanning for {target} in {len(files)} files...")

found_years = []

for fpath in files:
    year = fpath.split('_')[1] # Market_2017_Prices.json
    try:
        with open(fpath, 'r') as f:
            data = json.load(f)
            # data is dict
            keys = list(data.keys())
            # Check for substring
            matches = [k for k in keys if target in k]
            if matches:
                print(f"Found in {year} (File: {os.path.basename(fpath)}): Keys={matches}")
                # Print sample value
                print(f"  Value: {data[matches[0]]}")
    except Exception as e:
        pass

if found_years:
    print(f"\nStart Year: {min(found_years)}")
    print(f"Total Years: {len(found_years)}")
else:
    print("Not found in any Market Cache.")
