import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import requests
import json

try:
    r = requests.get("http://localhost:8000/api/race-data")
    data = r.json()
    if data:
        # Sort by ID to find the ones from screenshot
        # Rank 1 ID: 6240
        # Rank 16 ID: 6139
        
        target_6240 = [x for x in data if str(x['id']) == "6240"]
        target_6139 = [x for x in data if str(x['id']) == "6139"]
        
        print("--- ID 6240 (Rank 1 in Screenshot) ---")
        for i in target_6240[:5]: # First 5 years
            print(i)
        
        print("\n--- ID 6139 (Rank 16 in Screenshot) ---")
        for i in target_6139[:5]:
             print(i)

    else:
        print("No data found")
except Exception as e:
    print(e)
