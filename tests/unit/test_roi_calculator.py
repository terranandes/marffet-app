
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.services.roi_calculator import ROICalculator

class TestROICalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = ROICalculator()

    def test_calculate_metrics_basic(self):
        # Create a simple DF: 10% increase over 1 year (approx)
        dates = pd.date_range(start='2020-01-01', periods=253, freq='B') # ~1 year business days
        # Price goes from 100 to 110
        prices = np.linspace(100, 110, len(dates))
        df = pd.DataFrame({'close': prices}, index=dates)
        
        metrics = self.calculator.calculate_metrics(df)
        
        self.assertIsNotNone(metrics)
        self.assertAlmostEqual(metrics['total_return_pct'], 10.0, delta=0.1)
        # CAGR should be around 10% since it's about 1 year
        self.assertAlmostEqual(metrics['cagr_pct'], 10.0, delta=0.5) 
    
    def test_calculate_metrics_empty(self):
        df = pd.DataFrame()
        metrics = self.calculator.calculate_metrics(df)
        self.assertIsNone(metrics)

    def test_calculate_complex_simulation_basic(self):
        # Simulate simple price growth: 100 -> 110 -> 121 (10% per year)
        # Years: 2020, 2021, 2022
        data = [
            {'date': datetime(2020, 1, 2), 'year': 2020, 'close': 100, 'open': 100, 'high': 100, 'low': 100},
            {'date': datetime(2020, 12, 31), 'year': 2020, 'close': 100, 'open': 100, 'high': 100, 'low': 100},
            
            {'date': datetime(2021, 1, 4), 'year': 2021, 'close': 110, 'open': 110, 'high': 110, 'low': 110},
            {'date': datetime(2021, 12, 31), 'year': 2021, 'close': 110, 'open': 110, 'high': 110, 'low': 110},
            
            {'date': datetime(2022, 1, 3), 'year': 2022, 'close': 121, 'open': 121, 'high': 121, 'low': 121},
            {'date': datetime(2022, 12, 30), 'year': 2022, 'close': 121, 'open': 121, 'high': 121, 'low': 121},
        ]
        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)
        
        # Principal 100,000. Annual Inv 0.
        result = self.calculator.calculate_complex_simulation(
            df, start_year=2020, principal=100_000, annual_investment=0, buy_logic='FIRST_CLOSE'
        )
        
        # 2020: Buy 1000 shares at 100. Invested 100,000. Value 100,000.
        # 2021: Price 110. Value 1000 * 110 = 110,000.
        # 2022: Price 121. Value 1000 * 121 = 121,000.
        
        self.assertEqual(result['finalValue'], 121_000)
        self.assertEqual(result['totalCost'], 100_000)
        
        # Check history
        history = result['history']
        self.assertEqual(len(history), 3+1) # Initial + 3 years
        
        # Initial
        self.assertEqual(history[0]['year'], 2020)
        self.assertEqual(history[0]['value'], 100_000)
        
        # Year 2020
        self.assertEqual(history[1]['value'], 100_000) # Price end of 2020 is 100
        
        # Year 2022
        self.assertEqual(history[3]['year'], 2022)
        self.assertEqual(history[3]['value'], 121_000)
        
    def test_calculate_complex_simulation_with_cash_dividends(self):
        # 2020: Price 100.
        # 2021: Price 100. Div Cash 10.
        # 2022: Price 100.
        
        data = [
            {'date': datetime(2020, 1, 2), 'year': 2020, 'close': 100, 'open': 100},
            {'date': datetime(2021, 1, 4), 'year': 2021, 'close': 100, 'open': 100},
            {'date': datetime(2022, 1, 3), 'year': 2022, 'close': 100, 'open': 100},
        ]
        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)
        
        dividend_data = {
            2021: {'cash': 10.0, 'stock': 0.0}
        }
        
        result = self.calculator.calculate_complex_simulation(
            df, start_year=2020, principal=100_000, annual_investment=0, 
            dividend_data=dividend_data, buy_logic='FIRST_CLOSE'
        )
        
        # 2020: Buy 1000 shares.
        # 2021: 1000 shares * 10 cash = 10,000 cash div. Reinvest at avg price (100).
        # Adds 100 shares. Total 1100 shares.
        # End 2021 Value: 1100 * 100 = 110,000.
        
        history = result['history']
        h2021 = next(h for h in history if h['year'] == 2021)
        self.assertEqual(h2021['dividend'], 10_000)
        self.assertEqual(h2021['value'], 110_000)
        
    def test_calculate_complex_simulation_with_stock_dividends(self):
        # 2020: Price 100.
        # 2021: Price 100. Stock Div 1.0 (100 shares per 1000? No, 1.0 dollar means 10% stock div -> 100 stock div = 1 dollar par value?)
        # Wait, the logic is: stock_shares_add = current_shares * (stock_div_dollar / 10.0)
        # So if stock_div_dollar is 1.0, it is 1.0/10.0 = 0.1 => 10% stock dividend.
        
        data = [
            {'date': datetime(2020, 1, 2), 'year': 2020, 'close': 100, 'open': 100},
            {'date': datetime(2021, 1, 4), 'year': 2021, 'close': 100, 'open': 100},
        ]
        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)
        
        dividend_data = {
            2021: {'cash': 0.0, 'stock': 1.0} # 10% stock div
        }
        
        result = self.calculator.calculate_complex_simulation(
            df, start_year=2020, principal=100_000, annual_investment=0,
            dividend_data=dividend_data, buy_logic='FIRST_CLOSE'
        )
        
        # 2020: Buy 1000 shares.
        # 2021: 10% stock div. 1000 -> 1100 shares.
        # Value: 1100 * 100 = 110,000.
        
        history = result['history']
        h2021 = next(h for h in history if h['year'] == 2021)
        self.assertEqual(h2021['value'], 110_000)

    def test_calculate_yearly_cumulative_cagr(self):
        # 2020: 100
        # 2021: 110
        # 2022: 121
        data = [
            {'date': datetime(2020, 1, 2), 'year': 2020, 'close': 100, 'open': 100},
            {'date': datetime(2021, 1, 4), 'year': 2021, 'close': 110, 'open': 110},
            {'date': datetime(2022, 1, 3), 'year': 2022, 'close': 121, 'open': 121},
        ]
        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)
        
        results = self.calculator.calculate_yearly_cumulative_cagr(df, start_year=2020)
        
        # s2020e2021bao: 10%
        # s2020e2022bao: 10% (CAGR of 100->121 over 2 years is 10%)
        
        self.assertAlmostEqual(results['s2020e2021bao'], 10.0, delta=0.1)
        self.assertAlmostEqual(results['s2020e2022bao'], 10.0, delta=0.1)

if __name__ == '__main__':
    unittest.main()
