
import sys
import os
from pathlib import Path
import json
import pandas as pd
import numpy as np

# Mock Backend Environment
BASE_DIR = Path("/home/terwu01/github/martian")
sys.path.insert(0, str(BASE_DIR))

from app.project_tw.calculator import ROICalculator

def test_detail_logic(stock_id="2330", start_year=2006):
    print(f"Testing Simulation for {stock_id} from {start_year}...")
    
    rows = []
    current_max_year = 2026
    
    for year in range(start_year, current_max_year + 1):
         p_file = BASE_DIR / f"data/raw/Market_{year}_Prices.json"
         tpex_file = BASE_DIR / f"data/raw/TPEx_Market_{year}_Prices.json"
         
         p_data = {}
         if p_file.exists():
             with open(p_file, "r") as f: p_data.update(json.load(f))
         if tpex_file.exists():
             with open(tpex_file, "r") as f: p_data.update(json.load(f))
             
         if stock_id in p_data:
             node = p_data[stock_id]
             rows.append({
                 "year": year,
                 "open": node.get('first_open', node.get('start', 0)),
                 "close": node.get('end', 0),
                 "high": node.get('high', 0),
                 "low": node.get('low', 0)
             })

    if not rows:
        print("Error: No data rows found.")
        return

    df = pd.DataFrame(rows)
    print(f"Loaded DataFrame with {len(df)} rows.")
    # print(df.tail())

    calc = ROICalculator()
    try:
        res = calc.calculate_complex_simulation(
            df, start_year, 1_000_000, 60_000, {}, stock_id, buy_logic='FIRST_OPEN'
        )
        print("Calculation Success!")
        print("Result Keys:", list(res.keys()))
        
        # Test Serialization
        print("Testing JSON Serialization...")
        dump = json.dumps(res, default=str) # Allow str conversion if needed
        print("Serialization Success!")
        # print("Dump:", dump[:100])
        
    except Exception as e:
        print(f"CRITICAL FAULT: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_detail_logic()
