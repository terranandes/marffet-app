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
    # Fetch from local API
    url = "http://localhost:8000/api/race-data"
    print(f"Fetching from {url}...")
    r = requests.get(url)
    
    if r.status_code != 200:
        print(f"Failed: {r.status_code}")
        exit()
        
    data = r.json()
    
    # Filter for TSMC (2330)
    # The ID matches the string "2330"
    tsmc = [d for d in data if str(d['id']) == "2330"]
    
    # Sort by year
    tsmc.sort(key=lambda x: x['year'])
    
    print(f"--- TSMC (2330) Data Points: {len(tsmc)} ---")
    print(f"{'Year':<6} {'ROI (%)':<10} {'Value':<10}")
    print("-" * 30)
    
    for row in tsmc:
        # Check standard keys
        year = row.get('year', 'N/A')
        roi = row.get('roi', 'N/A')
        val = row.get('value', 'N/A')
        print(f"{year:<6} {roi:<10} {val:<10}")

    # Quick Wealth Simulation check
    # Principal: 1,000,000. Contrib: 60,000/yr.
    # Start: 2006.
    
    principal = 1000000
    contrib = 60000
    wealth = principal
    cost = principal
    
    print("\n--- Simulation Check ---")
    for row in tsmc:
        y = row['year']
        if y < 2006: continue
        
        roi_pct = row['roi']
        factor = 1 + (roi_pct / 100.0)
        
        wealth = wealth * factor
        wealth += contrib
        cost += contrib
        
        print(f"Year {y}: Factor={factor:.2f} Wealth={wealth:,.0f}")

except Exception as e:
    print(f"Error: {e}")
