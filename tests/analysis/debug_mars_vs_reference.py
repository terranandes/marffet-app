
import pandas as pd
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.strategy_service import MarsStrategy

REFERENCE_FILE = "app/project_tw/references/stock_list_s2006e2026_unfiltered.xlsx"

def load_reference(stock_id: str):
    print(f"Loading reference from {REFERENCE_FILE} (Stock: {stock_id})...")
    try:
        df = pd.read_excel(REFERENCE_FILE)
        # Assuming there is an 'id' or 'ID' column
        # Standardize column names
        df.columns = [c.lower() for c in df.columns]
        
        print("Columns:", df.columns.tolist())
        # IDs seem to be strings in the Excel
        # Ensure stock_id is string
        target_id = str(stock_id)
        
        # Check if column is int or str
        if df['id'].dtype == 'int64':
             row = df[df['id'] == int(stock_id)]
        else:
             # Convert column to string just in case
             df['id'] = df['id'].astype(str)
             row = df[df['id'] == target_id]
        if row.empty:
            print(f"Stock {stock_id} not found in reference!")
            return None
        return row.iloc[0].to_dict()
    except Exception as e:
        print(f"Error loading reference: {e}")
        return None

async def run_simulation(stock_id: str):
    print(f"Running StrategyService for {stock_id}...")
    strategy = MarsStrategy()
    # Parameters match the filename s2006e2026 -> Start 2006
    # Standard: 1M Principal, 60k Annual
    # Note: verify if Year 2026 is included in Reference? 
    # Filename says 2026, but current mock data might only go to 2025?
    # Let's try to match 2006-2025 first if 2026 not available.
    
    # We use await because analyze might be async in future, but currently it's sync wrapped?
    # Wait, MarsStrategy.analyze is async def?
    # Let's check source code.
    # It is async def analyze(self, ...)
    
    results = await strategy.analyze(
        stock_ids=[stock_id],
        start_year=2006
    )
    
    # Extract specific stock result
    # It seems StrategyService uses 'stock_code'
    for res in results:
        # print("Result keys:", res.keys()) # Debug if needed
        # Use .get to be safe
        res_id = res.get('stock_code') or res.get('id')
        if str(res_id) == str(stock_id):
            return res
            
    print(f"Stock {stock_id} not found in strategy results!")
    return None

import asyncio

async def main():
    target_stock = "2330" # TSMC
    
    ref_data = load_reference(target_stock)
    if not ref_data:
        return

    sim_data = await run_simulation(target_stock)
    if not sim_data:
        return

    print("\n" + "="*50)
    print(f"COMPARISON FOR STOCK {target_stock}")
    print("="*50)
    
    # Keys might differ, need to map them
    # Excel likely has: 'Final Value', 'CAGR %', 'ROI %', 'Total Cost'
    
    # Print Reference
    print("\n--- REFERENCE (Excel) ---")
    # Print all keys to help identify structure
    for k, v in ref_data.items():
        if "final" in str(k) or "cagr" in str(k) or "roi" in str(k) or "value" in str(k):
             print(f"{k}: {v}")

    # Print Strategy
    print("\n--- STRATEGY (Code) ---")
    print(f"Final Value: {sim_data.get('finalValue')}")
    print(f"CAGR: {sim_data.get('cagr_pct')}%")
    print(f"ROI: {sim_data.get('roi_pct')}%")
    print(f"Total Cost: {sim_data.get('totalCost')}")
    
    # Deep Dive into History?
    # Strategy returns history? No, analyze() returns summary list.
    # analyze_detail() returns history.
    
    # Print Strategy
    print("\n--- STRATEGY (Code) ---")
    print(f"Final Value: {sim_data.get('finalValue')}")
    print(f"CAGR: {sim_data.get('cagr_pct')}%")
    print(f"ROI: {sim_data.get('roi_pct')}%")
    print(f"Total Cost: {sim_data.get('totalCost')}")
    print(f"Duration Items: {sim_data.get('s2006e2025yrs')}") # Debug duration
    
    # Check intermediate keys
    keys = sorted([k for k in sim_data.keys() if k.startswith('s2006')])
    print("Intermediate Keys Found:", len(keys))
    # print(keys[:5])

if __name__ == "__main__":
    asyncio.run(main())
