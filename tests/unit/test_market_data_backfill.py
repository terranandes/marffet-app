
import unittest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
import json
from pathlib import Path

# Adjust path to import app
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.services.market_data_service import backfill_all_stocks

class TestBackfill(unittest.TestCase):
    @patch('app.services.market_data_service.pd.read_csv')
    @patch('app.services.market_data_service.yf.download')
    @patch('builtins.open', new_callable=mock_open)
    @patch('app.services.market_data_service.json.dump')
    def test_backfill_flow(self, mock_json_dump, mock_file_open, mock_yf, mock_read_csv):
        # 1. Mock Stock List
        mock_df = pd.DataFrame([
            {'code': '1101', 'name': 'TCC', 'market_type': 'Listed'},
            {'code': '8044', 'name': 'PChome', 'market_type': 'OTC'}
        ])
        mock_read_csv.return_value = mock_df

        # 2. Mock YFinance Data
        # Create MultiIndex DataFrame: (Ticker, PriceType)
        dates = pd.date_range(start='2024-01-01', periods=2)
        
        # 1101.TW Data
        arrays_1 = [['1101.TW']*5, ['Open', 'High', 'Low', 'Close', 'Volume']]
        tuples_1 = list(zip(*arrays_1))
        index_1 = pd.MultiIndex.from_tuples(tuples_1, names=['Ticker', 'Price'])
        data_1 = pd.DataFrame([[40.0, 42.0, 39.0, 41.0, 1000], [41.0, 43.0, 40.0, 42.0, 2000]], index=dates, columns=index_1)
        
        # 8044.TWO Data
        arrays_2 = [['8044.TWO']*5, ['Open', 'High', 'Low', 'Close', 'Volume']]
        tuples_2 = list(zip(*arrays_2))
        index_2 = pd.MultiIndex.from_tuples(tuples_2, names=['Ticker', 'Price'])
        data_2 = pd.DataFrame([[100.0, 102.0, 99.0, 101.0, 500], [101.0, 103.0, 100.0, 102.0, 600]], index=dates, columns=index_2)
        
        # Combine
        mock_yf_data = pd.concat([data_1, data_2], axis=1)
        mock_yf.return_value = mock_yf_data
        
        # 3. Validation Logic
        # We need to ensure the file writing logic is triggered.
        # backfill_all_stocks writes to "data/raw/Market_{Year}_Prices.json"
        
        # Run
        result = backfill_all_stocks(period="1mo")
        
        # Verify Function Return
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['stocks_processed'], 2)
        # We have data for 2024 only
        self.assertEqual(result['years_covered'], 1)
        
        # Verify JSON Dump
        # Provide check that json.dump was called
        # once for TWSE (1101) and once for TPEx (8044) for year 2024
        self.assertTrue(mock_json_dump.called)
        self.assertEqual(mock_json_dump.call_count, 2)
        
        # Verify Content of Dump
        # Args: (data, file_handle, indent=None)
        # We can inspect the first arg of the calls
        dump_calls = mock_json_dump.call_args_list
        
        # We expect one dict to contain '1101' and another '8044'
        content_1 = dump_calls[0][0][0]
        content_2 = dump_calls[1][0][0]
        
        combined_keys = list(content_1.keys()) + list(content_2.keys())
        self.assertIn('1101', combined_keys)
        self.assertIn('8044', combined_keys)
        
        print("Backfill test passed!")

if __name__ == '__main__':
    unittest.main()
