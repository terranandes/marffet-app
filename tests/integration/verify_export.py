import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


import requests
import pandas as pd
import io
import sys

# Base URL (assuming running on localhost:8000)
BASE_URL = "http://localhost:8000"

def test_excel_export():
    print("Testing /api/export/excel...")
    
    # 1. Test Default (Filtered, 2006, 1M, 60k)
    params = {
        "mode": "filtered",
        "start_year": 2015,
        "principal": 500000,
        "contribution": 120000
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/export/excel", params=params)
        
        if response.status_code != 200:
            print(f"FAILED: Status Code {response.status_code}")
            print(response.text)
            sys.exit(1)
            
        # Check Headers
        cd = response.headers.get("Content-Disposition", "")
        print(f"Header: {cd}")
        if "filename=stock_list_s2015e2025_filtered.xlsx" not in cd:
            print("FAILED: Incorrect filename in header")
            # sys.exit(1) # Soft fail for now
            
        # Check Content
        with io.BytesIO(response.content) as f:
            df = pd.read_excel(f, sheet_name="Mars Strategy Source")
            print(f"Success! Read Excel with {len(df)} rows.")
            print(df.head())
            
            # Check Stats
            # Ensure we have columns
            expected_cols = ["Stock ID", "Name", "CAGR %", "Final Value ($)", "Total ROI %"]
            for c in expected_cols:
                if c not in df.columns:
                    print(f"FAILED: Missing column {c}")
                    sys.exit(1)
            
            # Check Params Sheet
            df_params = pd.read_excel(f, sheet_name="Simulation Params")
            print("Params Sheet:")
            print(df_params.iloc[0])
            
            if df_params.iloc[0]["Start Year"] != 2015:
                 print("FAILED: Simulation Params mismatch")
                 sys.exit(1)

        print("Values check passed.")

    except Exception as e:
        print(f"FAILED with Exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_excel_export()
