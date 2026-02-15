import json
import os
import sys

# Ensure we can import app
sys.path.append(os.getcwd())

from app.services.market_db import get_connection

def verify_cagr(stock_id, start_year=2006, end_year=2025, principal=1000000):
    with open('data/yearly_nominal_prices.json', 'r') as f:
        prices = json.load(f)
    
    conn = get_connection(read_only=True)
    divs = conn.execute("SELECT year, cash, stock FROM dividends WHERE stock_id = ?", [stock_id]).fetchall()
    div_map = {r[0]: {'cash': r[1], 'stock': r[2]} for r in divs}
    conn.close()

    # Simulation
    shares = 0
    cash = principal
    
    # 1. First Buy
    start_p = prices.get(str(start_year), {}).get(stock_id)
    if not start_p:
        # Try next year if上市 late
        while start_year <= end_year and not prices.get(str(start_year), {}).get(stock_id):
            start_year += 1
        start_p = prices.get(str(start_year), {}).get(stock_id)
        
    if not start_p:
        return None

    shares = cash / start_p
    cash = 0
    
    print(f"--- Simulating {stock_id} ---")
    print(f"Year {start_year}: Buy at {start_p}, Shares={shares:.2f}")

    years_run = 0
    for y in range(start_year, end_year + 1):
        years_run += 1
        # Apply Dividends for previous year results (or current)
        d = div_map.get(y, {'cash':0, 'stock':0})
        p = prices.get(str(y), {}).get(stock_id, start_p) # Snapshot price
        
        # Stock Div
        if d['stock'] > 0:
            shares *= (1 + d['stock']/10)
            
        # Cash Div Reinvest
        if d['cash'] > 0:
            dividend_cash = shares * d['cash']
            shares += dividend_cash / p
            
    final_p = prices.get(str(end_year), {}).get(stock_id, p)
    final_value = shares * final_p
    cagr = (final_value / principal) ** (1/years_run) - 1
    
    print(f"Final Year {end_year}: Price={final_p}, Shares={shares:.2f}")
    print(f"Final Value: {final_value:,.0f}")
    print(f"CAGR: {cagr*100:.2f}%")
    return cagr*100

if __name__ == "__main__":
    verify_cagr('2330') # TSMC
    verify_cagr('4763', 2016) # Materials-KY
