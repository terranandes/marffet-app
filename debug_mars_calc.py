
import time
import pandas as pd
from app.services.market_cache import MarketCache
from app.project_tw.calculator import ROICalculator
from app.main import DIVIDENDS_DB, init_db

def benchmark_calc():
    print("--- 1. Warming Up ---")
    t0 = time.time()
    init_db() # Should be fast
    MarketCache.get_prices_db(force_reload=True) # Heavy Lift
    print(f"Warmup Time: {time.time()-t0:.4f}s")
    
    stock_id = "2330"
    start_year = 2006
    principal = 1000000
    contribution = 60000
    
    print(f"\n--- 2. Fetching History ---")
    t0 = time.time()
    history = MarketCache.get_stock_history_fast(stock_id)
    fetch_time = time.time() - t0
    print(f"History Fetch: {fetch_time:.6f}s (Rows: {len(history)})")
    
    calc = ROICalculator()
    
    # Simulate API logic
    rows = [h for h in history if h['year'] >= start_year]
    df = pd.DataFrame(rows)
    div_data = DIVIDENDS_DB.get(stock_id, {})
    
    print(f"\n--- 3. Running Calculations (3 Strategies) ---")
    t0 = time.time()
    
    strategies = ['FIRST_OPEN', 'YEAR_HIGH', 'YEAR_LOW']
    for strat in strategies:
        t_strat = time.time()
        res = calc.calculate_complex_simulation(df, start_year, principal, contribution, div_data, stock_id, buy_logic=strat)
        print(f"  > {strat}: {time.time()-t_strat:.6f}s")
        
    total_calc_time = time.time() - t0
    print(f"Total Calc Time: {total_calc_time:.6f}s")
    
    if total_calc_time > 1.0:
        print("\n[FAIL] Calculation is Slow (>1s).")
    else:
        print("\n[PASS] Calculation is Fast.")

if __name__ == "__main__":
    benchmark_calc()
