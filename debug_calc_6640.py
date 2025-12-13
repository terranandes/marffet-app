import pandas as pd
from project_tw.calculator import ROICalculator

def test_calc():
    calc = ROICalculator()
    
    # Mock Data for 6640
    # 2017: 50 -> 50
    # 2024: 147 -> 640
    # Fill in between roughly
    data = [
        {'date': pd.Timestamp('2017-01-02'), 'open': 50.0, 'close': 50.0},
        {'date': pd.Timestamp('2018-01-02'), 'open': 50.0, 'close': 60.0},
        {'date': pd.Timestamp('2024-01-02'), 'open': 147.0, 'close': 640.0},
        {'date': pd.Timestamp('2025-01-02'), 'open': 640.0, 'close': 640.0},
    ]
    df = pd.DataFrame(data).set_index('date')
    
    divs = {
        2017: {'cash':0, 'stock':0}, 
        2024: {'cash':0, 'stock':0}
    }
    
    res = calc.calculate_complex_simulation(df, 2006, dividend_data=divs, stock_code='6640')
    print(res)

test_calc()
