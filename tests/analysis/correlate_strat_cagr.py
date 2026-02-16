import sys
import os
from pathlib import Path
import pandas as pd
import logging

# Setup Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.services.market_cache import MarketCache
from app.project_tw.calculator import ROICalculator
from app.services.market_data_provider import MarketDataProvider

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def run_correlation(stock_id: str, name: str):
    logging.info(f"--- Correlating {name} ({stock_id}) ---")
    
    # 1. Fetch History (Clean Room / Cached)
    history = MarketCache.get_stock_history_fast(stock_id)
    if not history:
        logging.error("No data found!")
        return
        
    df = pd.DataFrame(history)
    df['year'] = df['year'].astype(int)
    
    # 2. Run Engine (Mars Strategy Logic)
    # Simulator: Buy Year 1 (1M) + 60k/yr.
    # Logic: First Open (BAO)
    calc = ROICalculator()
    start_year = 2006
    
    # Dividend Data
    div_data = MarketDataProvider.load_dividends_dict().get(stock_id, {})
    
    res = calc.calculate_complex_simulation(
        df, 
        start_year=start_year, 
        principal=1_000_000, 
        annual_investment=60_000, 
        dividend_data=div_data, 
        stock_code=stock_id,
        buy_logic='FIRST_OPEN'
    )
    
    # 3. Output Metrics
    final_val = res.get('finalValue', 0)
    cost = res.get('totalCost', 0)
    cagr_col = f"s{start_year}e2026bao" # 2026 is last year in cache logic for now?
    # Ensure we get the actual last year key
    keys = [k for k in res.keys() if 'bao' in k]
    if keys:
        last_bao = keys[-1] # Usually sorted? Dictionary order not guaranteed.
        # Find max year
        max_y = 0
        target_k = ""
        for k in keys:
            # s2006e2025bao
            y_part = int(k.split('e')[1].split('bao')[0])
            if y_part > max_y:
                max_y = y_part
                target_k = k
        
        cagr = res.get(target_k, 0)
        logging.info(f"Period: {start_year}-{max_y}")
        logging.info(f"Total Cost: ${cost:,.0f}")
        logging.info(f"Final Value: ${final_val:,.0f}")
        logging.info(f"CAGR (Engine): {cagr}%")
        
        # Simple "MoneyCome" Benchmark/Heuristic
        # TSMC ~18-22%? 0050 ~8-9%? 
        # Wealth Verification: 
        # MoneyCome 2330 (2006-2023) was ~15-20%.
        
    else:
        logging.error("No CAGR calculated.")

def main():
    # Warm Cache
    MarketCache.get_prices_db() 
    
    run_correlation("2330", "TSMC")
    run_correlation("0050", "Yuanta 50")

if __name__ == "__main__":
    main()
