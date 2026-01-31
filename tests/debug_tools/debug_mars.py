import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

#!/usr/bin/env python3
"""Simulate EXACTLY what run_mars_simulation does for stock 6584."""

import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def main():
    # Load Excel
    SOURCE_FILE = BASE_DIR / "project_tw/references/stock_list_s2006e2026_filtered.xlsx"
    df = pd.read_excel(SOURCE_FILE)
    df = df.fillna(0)
    
    # Load Prices
    PRICES_DB = {}
    for year in range(2006, 2027):
        p_file = BASE_DIR / f"data/raw/Market_{year}_Prices.json"
        if p_file.exists():
            with open(p_file, "r") as f:
                PRICES_DB[year] = json.load(f)
        tpex_file = BASE_DIR / f"data/raw/TPEx_Market_{year}_Prices.json"
        if tpex_file.exists():
            with open(tpex_file, "r") as f:
                if year not in PRICES_DB:
                    PRICES_DB[year] = {}
                PRICES_DB[year].update(json.load(f))
    
    # Load Dividends (simplified - just hardcode)
    DIVIDENDS_DB = {}
    dividends_file = BASE_DIR / "data/dividends_all.json"
    if dividends_file.exists():
        with open(dividends_file, "r") as f:
            DIVIDENDS_DB = json.load(f)
    
    # Simulation Parameters
    start_year = 2006
    principal = 1_000_000
    contribution = 60_000
    
    # Target stock
    stock_id = '6584'
    row = df[df['id'].astype(str) == stock_id].iloc[0]
    
    print(f"=== Simulating {stock_id}: {row['name']} ===")
    print(f"Start: {start_year}, Principal: {principal}, Contribution: {contribution}")
    
    # Year cols
    year_cols = [c for c in df.columns if 'bao' in c]
    
    # Simulation state
    shares = 0
    cost = 0
    wealth = 0
    prev_wealth = 0
    wealth_trend = []
    
    # Initial purchase
    start_price_initial = PRICES_DB.get(start_year, {}).get(stock_id, {}).get('start', 0)
    print(f"\nInitial start_price ({start_year}): {start_price_initial}")
    
    cost = principal
    prev_wealth = principal
    shares = 0
    
    if start_price_initial > 0:
        shares = principal / start_price_initial
        print(f"Initial shares: {shares:.2f}")
    else:
        print(f"Initial shares: 0 (no price data for {start_year})")
    
    print(f"\n{'Year':<6} {'Branch':<12} {'Shares':<12} {'Wealth':<15} {'prev_wealth':<15}")
    print("-" * 70)
    
    for col in year_cols:
        try:
            year_str = col.split('e')[1][:4]
            year = int(year_str)
            
            if year < start_year:
                continue
            
            excel_roi = row[col]
            
            y_data = PRICES_DB.get(year, {}).get(stock_id, {})
            start_price = y_data.get('start', 0)
            end_price = y_data.get('end', 0)
            
            div_cash = 0  # Initialize here!
            
            if start_price > 0:
                branch = "REAL"
                
                # Transition from synthetic
                if shares == 0:
                    shares = prev_wealth / start_price
                    print(f"  *** TRANSITION: shares = {prev_wealth} / {start_price} = {shares:.2f}")
                
                # Get dividend
                div_info = DIVIDENDS_DB.get(stock_id, {}).get(str(year)) or DIVIDENDS_DB.get(stock_id, {}).get(year, {})
                if isinstance(div_info, dict):
                    div_cash = div_info.get('cash', 0)
                elif isinstance(div_info, (int, float)):
                    div_cash = div_info
                
                # Cash dividend
                cash_received = shares * div_cash
                
                if end_price == 0:
                    end_price = start_price * (1 + excel_roi/100)
                
                avg_price = (start_price + end_price) / 2
                
                total_cash_in = cash_received + contribution
                new_shares_bought = total_cash_in / avg_price
                
                shares += new_shares_bought
                cost += contribution
                
                wealth = shares * end_price
                prev_wealth = wealth
            else:
                branch = "SYNTHETIC"
                wealth = prev_wealth * (1 + excel_roi/100) + contribution
                prev_wealth = wealth
                cost += contribution
            
            wealth_trend.append({
                "year": year,
                "value": round(wealth, 0),
                "dividend": round(div_cash * shares, 0)
            })
            
            print(f"{year:<6} {branch:<12} {shares:<12.2f} ${wealth:<14,.0f} ${prev_wealth:<14,.0f}")
            
        except Exception as e:
            print(f"Error at year {year}: {e}")
    
    print(f"\n=== FINAL ===")
    print(f"Final Wealth: ${wealth:,.0f}")
    print(f"Total Cost: ${cost:,.0f}")
    print(f"ROI: {((wealth - cost) / cost * 100):.2f}%")
    print(f"Years in wealth_trend: {len(wealth_trend)}")

if __name__ == "__main__":
    main()
