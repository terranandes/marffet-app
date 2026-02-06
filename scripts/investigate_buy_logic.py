
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.project_tw.calculator import ROICalculator
from app.services.market_cache import MarketCache
import pandas as pd

def test_logic():
    stock_id = "0050"
    print(f"Testing Buy Logic for {stock_id}...")
    
    # Load Data
    history = MarketCache.get_stock_history_fast(stock_id)
    if not history:
        print("No history found!")
        return
        
    df = pd.DataFrame(history)
    
    # Load Divs
    from app.main import DIVIDENDS_DB
    div_data = DIVIDENDS_DB.get(stock_id, {})
    
    calc = ROICalculator()
    
    # Test 1: FIRST_OPEN
    res_open = calc.calculate_complex_simulation(
        df=df.copy(),
        start_year=2006,
        principal=1_000_000,
        annual_investment=60_000,
        dividend_data=div_data,
        stock_code=stock_id,
        buy_logic='FIRST_OPEN'
    )
    cagr_open = res_open.get(f"s2006e2026bao", 0)
    
    # Test 2: FIRST_CLOSE
    res_close = calc.calculate_complex_simulation(
        df=df.copy(),
        start_year=2006,
        principal=1_000_000,
        annual_investment=60_000,
        dividend_data=div_data,
        stock_code=stock_id,
        buy_logic='FIRST_CLOSE'
    )
    cagr_close = res_close.get(f"s2006e2026bao", 0)
    
    print("\n" + "="*40)
    print(f"Target (MoneyCome): 10.50%")
    print("="*40)
    print(f"FIRST_OPEN  (Current): {cagr_open}%")
    print(f"FIRST_CLOSE (Proposed): {cagr_close}%")
    print("="*40)
    
    diff_open = abs(cagr_open - 10.5)
    diff_close = abs(cagr_close - 10.5)
    
    if diff_close < diff_open:
        print("\n✅ FIRST_CLOSE is closer! We should switch.")
    else:
        print("\n❌ FIRST_OPEN is closer. Keep it.")

if __name__ == "__main__":
    test_logic()
