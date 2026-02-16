import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


import pandas as pd
import json
import os
import random
import numpy as np
from app.services.market_data_provider import MarketDataProvider

# Paths
EXCEL_PATH = 'project_tw/references/stock_list_s2006e2026_filtered.xlsx'
DATA_DIR = 'data/raw'

def load_prices_db():
    PRICES_DB = {}
    print("Loading Price Data...")
    for year in range(2006, 2026):
        p_file = f"{DATA_DIR}/Market_{year}_Prices.json"
        if os.path.exists(p_file):
            with open(p_file, "r") as f:
                PRICES_DB[year] = json.load(f)
        else:
            PRICES_DB[year] = {}
            
        tpex_file = f"{DATA_DIR}/TPEx_Market_{year}_Prices.json"
        if os.path.exists(tpex_file):
            pass # TODO: Add TPEx loading if needed for full coverage, but standard market is fine for test
            with open(tpex_file, "r") as f:
                PRICES_DB[year].update(json.load(f))
    return PRICES_DB

def calculate_roi_sim(stock_id, start_year, end_year, prices_db):
    """
    Simulates 'Mars Strategy':
    - Start with Principal (e.g. 1M)
    - Buy at Start Price of Year 1
    - Annually:
        - Add Contribution (60k) ? No, per user desc 'bao' usually means simple CAGR or specific rule.
        - Let's matching the 'Generalized Share Accumulation' from main.py logic 
          BUT stripped down to specific period.
    - However, user said 's2006e2007bao' = 'Buy at Opening for Extra Investment'.
    - Let's attempt to match the EXACT logic in main.py's get_race_data loop.
    """
    
    SIM_PRINCIPAL = 1_000_000
    SIM_CONTRIB = 0 # Golden Excel usually assumes Lump Sum or specific rule?
    # User said "bao means buy at opening for extra investment per year" -> likely SIM_CONTRIB exists.
    # In main.py: SIM_CONTRIB = 60_000 is hardcoded.
    
    SIM_CONTRIB = 60_000
    
    shares = 0
    cost = 0
    wealth = 0
    
    # 1. Initial Buy (Start Year)
    start_market_data = prices_db.get(start_year, {}).get(str(stock_id))
    if not start_market_data:
        return None # No data
        
    price_0 = start_market_data.get('start', 0)
    if price_0 <= 0:
        return None
        
    shares = SIM_PRINCIPAL / price_0
    cost = SIM_PRINCIPAL
    
    current_year = start_year
    
    # Loop from start_year to end_year
    # Note: Excel columns like s2006e2007 means result AT END 2007.
    # So we loop year 2006, 2007...
    
    for year in range(start_year, end_year + 1):
        if year >= 2026: break # No price data for 2026 yet
        
        y_data = prices_db.get(year, {}).get(str(stock_id))
        if not y_data:
            continue
            
        start_price = y_data.get('start', 0)
        end_price = y_data.get('end', 0)
        
        if start_price <= 0: continue
        
        # 1. Dividend Reinvestment & Split
        # Helper from main.py logic? We'll re-implement simple version
        div_info = MarketDataProvider.load_dividends_dict().get(str(stock_id), {}).get(str(year))
        
        cash_div = 0
        stock_div = 1.0
        
        if isinstance(div_info, dict):
            cash_div = div_info.get('cash', 0)
            stock_div = div_info.get('stock_split', 1.0)
        elif isinstance(div_info, (int, float)):
            cash_div = div_info
            
        # A. Stock Split
        shares *= stock_div
        
        # B. Cash Div Reinvestment (at Start Price of NEXT year? Or End of This Year?)
        # main.py logic: uses 'start_price' of current year for 'extra invest'?
        # Actually main.py adds 60k at START of year.
        
        # Add Annual Contribution (Buy at Start)
        if year > start_year: # Don't double count initial
            new_shares = SIM_CONTRIB / start_price
            shares += new_shares
            cost += SIM_CONTRIB
            
        # Reinvest Dividends (Cash Div * Shares) -> Buy more shares
        # Usually assumed buy at average or end?
        # Let's assume Buy at Start for simplicity or End?
        # main.py code checks: 
        #   total_div = shares * div_cash
        #   shares += total_div / end_price (Reinvest at End Price usually)
        
        total_cash_div = shares * cash_div
        if end_price > 0:
            shares += total_cash_div / end_price
            
        # Update Wealth
        wealth = shares * end_price
        
    if cost == 0: return 0
    roi = ((wealth - cost) / cost) * 100
    return roi

def verify():
    print(f"Loading Excel: {EXCEL_PATH}...")
    df = pd.read_excel(EXCEL_PATH)
    prices_db = load_prices_db()
    
    # Select random samples
    samples = df.sample(n=20)
    
    print(f"\n🔍 Verifying 20 Random Targets (Sim vs Excel s2006e2025bao)...")
    print(f"{'Stock':<10} {'Excel ROI':<12} {'Sim ROI':<12} {'Diff':<10}")
    print("-" * 50)
    
    correlations = []
    
    for _, row in samples.iterrows():
        sid = row['id']
        
        # Target Column: s2006e2025bao
        # We verify the FULL period 2006-2025
        col_name = 's2006e2025bao' 
        if col_name not in row:
            continue
            
        excel_roi = row[col_name]
        
        # Run Sim
        try:
            # Note: Excel might handle 'NaN' as 0
            if pd.isna(excel_roi): excel_roi = 0
            
            sim_roi = calculate_roi_sim(sid, 2006, 2025, prices_db)
            
            if sim_roi is None:
                # If we have no data, Excel should be 0 or NaN?
                sim_roi = 0
                
            diff = abs(sim_roi - excel_roi)
            print(f"{sid:<10} {excel_roi:<12.2f} {sim_roi:<12.2f} {diff:<10.2f}")
            
            correlations.append((excel_roi, sim_roi))
            
        except Exception as e:
            print(f"Error {sid}: {e}")

    # Calc Stats
    valid = [x for x in correlations if x[1] != 0] # Filter zeroes if needed
    if not valid:
        print("No valid data points.")
        return

    x = np.array([v[0] for v in valid])
    y = np.array([v[1] for v in valid])
    
    corr = np.corrcoef(x, y)[0, 1]
    print("-" * 50)
    print(f"✅ Correlation Coefficient: {corr:.4f}")

if __name__ == "__main__":
    verify()
