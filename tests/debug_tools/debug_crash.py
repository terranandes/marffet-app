
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.project_tw.calculator import ROICalculator
from app.services.market_cache import MarketCache
import pandas as pd
import json
import traceback

def safe_json_dump(data):
    try:
        json.dumps(data)
        print("JSON Serialization Check: OK")
    except Exception as e:
        print(f"JSON Serialization Check: FAILED - {e}")
        # recursively find the bad item
        # ignored for brevity in this crash reproduction script, we just want to see if it crashes

def debug_crash():
    print("Reproducing API Crash...")
    try:
        # Load Data
        stock_ids = ["0050", "2330", "2884"] # Try a few known stocks
        
        calc = ROICalculator()
        
        # Mock Dividends
        div_data = {}
        
        results = []
        
        for stock_id in stock_ids:
            print(f"Processing {stock_id}...")
            history = MarketCache.get_stock_history_fast(stock_id)
            if not history:
                print(f"  No history for {stock_id}")
                continue
            
            df = pd.DataFrame(history)
            if 'year' not in df.columns:
                df['year'] = df['year'].astype(int)
            
            # Run simulation
            sim_res = calc.calculate_complex_simulation(
                df, 
                start_year=2006, 
                principal=1_000_000, 
                contribution=60_000, 
                dividend_data=div_data.get(stock_id, {}), 
                stock_code=stock_id, 
                buy_logic='FIRST_CLOSE'
            )
            
            # Construct API-like response
            if sim_res:
                final_val = sim_res.get('finalValue', 0)
                total_cost = sim_res.get('totalCost', 0)
                hist_list = sim_res.get('history', [])
                
                res_entry = {
                    "id": stock_id,
                    "name": f"Stock {stock_id}",
                    "finalValue": final_val,
                    "totalCost": total_cost,
                    "cagr_pct": 0,
                    "history": hist_list
                }
                
                # Copy simulated CAGR keys
                for k, v in sim_res.items():
                    if k.startswith('s') and 'bao' in k:
                        res_entry[k] = v
                
                results.append(res_entry)
        
        print(f"Simulation done. Generated {len(results)} results.")
        
        # Test Serialization (The likely culprit)
        print("Testing JSON Serialization...")
        json_str = json.dumps(results)
        print("Serialization Success!")
        
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    debug_crash()
