
import sys
import os
sys.path.append(os.getcwd()) # Add project root to path

from unittest.mock import MagicMock
sys.modules['yfinance'] = MagicMock() # Mock missing dependency globally

import unittest
from unittest.mock import patch
from app.engines import RuthlessManager
from app import portfolio_db

# Mock Data
MOCK_USER_ID = "test_user"
MOCK_TARGET_ID = "t1"
MOCK_STOCK_ID = "2330"

class TestNotifications(unittest.TestCase):

    def setUp(self):
        # Patchers
        self.patcher_get = patch('app.portfolio_db.get_all_targets_by_type')
        self.patcher_prices = patch('app.portfolio_db.fetch_live_prices')
        self.patcher_notify = patch('app.portfolio_db.create_notification')
        self.patcher_ticker = patch('yfinance.Ticker')

        self.mock_get = self.patcher_get.start()
        self.mock_prices = self.patcher_prices.start()
        self.mock_notify = self.patcher_notify.start()
        self.mock_ticker = self.patcher_ticker.start()

    def tearDown(self):
        self.patcher_get.stop()
        self.patcher_prices.stop()
        self.patcher_notify.stop()
        self.patcher_ticker.stop()

    def test_gravity_alert_sell_euphoria(self):
        """Test Gravity Alert: Price > 1.2 * SMA"""
        # Setup
        self.mock_get.return_value = {
            'stock': [{'id': MOCK_TARGET_ID, 'stock_id': MOCK_STOCK_ID, 'stock_name': 'TSMC', 'total_shares': 1000}]
        }
        self.mock_prices.return_value = {
            MOCK_STOCK_ID: {'price': 130} # Current Price
        }
        
        # Mock yfinance inside check_gravity_alert
        # SMA = 100. 1.2 * 100 = 120. Price 130 > 120 -> ALERT
        instance = self.mock_ticker.return_value
        instance.fast_info = {'lastPrice': 130, 'twoHundredDayAverage': 100}
        
        # Run
        RuthlessManager.run_checks(MOCK_USER_ID)
        
        # Verify
        self.mock_notify.assert_called_with(
            MOCK_USER_ID, 'GRAVITY', 
            'Gravity Alert: TSMC Euphoria', 
            'Price (130) is > 20% above SMA250 (100). Sell the euphoria.', 
            target_id=MOCK_TARGET_ID
        )

    def test_gravity_alert_buy_fear(self):
        """Test Gravity Alert: Price < 0.8 * SMA"""
        self.mock_get.return_value = {
            'stock': [{'id': MOCK_TARGET_ID, 'stock_id': MOCK_STOCK_ID, 'stock_name': 'TSMC', 'total_shares': 1000}]
        }
        self.mock_prices.return_value = {
            MOCK_STOCK_ID: {'price': 70} 
        }
        
        # SMA = 100. 0.8 * 100 = 80. Price 70 < 80 -> ALERT
        instance = self.mock_ticker.return_value
        instance.fast_info = {'lastPrice': 70, 'twoHundredDayAverage': 100}
        
        RuthlessManager.run_checks(MOCK_USER_ID)
        
        args = self.mock_notify.call_args[0]
        self.assertIn("Fear", args[2])

    def test_size_authority_overweight(self):
        """Test Size Authority: Cap > 1.2 * Avg"""
        # 2 Targets. Avg Cap needs to be calculated.
        # T1: 1000 shares * $10 = $10,000
        # T2: 1000 shares * $50 = $50,000 (Giant)
        # Total = 60000. Avg = 30000. 
        # T2 is 50000. 1.2 * 30000 = 36000. 50k > 36k -> ALERT for T2.
        
        self.mock_get.return_value = {
            'stock': [
                {'id': 't1', 'stock_id': '1101', 'stock_name': 'Cement', 'total_shares': 1000},
                {'id': 't2', 'stock_id': '2330', 'stock_name': 'TSMC', 'total_shares': 1000}
            ]
        }
        self.mock_prices.return_value = {
            '1101': {'price': 10},
            '2330': {'price': 50}
        }
        
        # Run
        # We need to make sure Gravity logic doesn't interfere or throw
        # Since we mocked yfinance, it shouldn't
        instance = self.mock_ticker.return_value
        instance.fast_info = {'lastPrice': 0, 'twoHundredDayAverage': 0} # Dummy

        RuthlessManager.run_checks(MOCK_USER_ID)
        
        # Check calls
        calls = self.mock_notify.call_args_list
        found = False
        for call in calls:
            args = call[0]
            kwargs = call[1]
            if args[1] == 'SIZE' and 'Overweight' in args[2] and kwargs.get('target_id') == 't2':
                found = True
        self.assertTrue(found, "Did not find Size Authority Overweight alert for t2")

    def test_cooldown_returns_false(self):
        """Verify create_notification returns False if duplicate exists"""
        # Unpatch notify since we want to test the REAL function this time?
        # No, 'create_notification' is a standalone function.
        # But we previously patched it in setUp.
        # We need to unpatch it for this specific test OR invoke the original.
        # It's cleaner to mock the DB inside create_notification.
        
        self.patcher_notify.stop() # Enable real function
        
        with patch('app.portfolio_db.get_db') as mock_ctx:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_ctx.return_value.__enter__.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock COUNT(*) > 0 (Duplicate exists)
            mock_cursor.fetchone.return_value = [1] 
            
            result = portfolio_db.create_notification("u1", "GRAVITY", "Title", "Msg", "t1")
            self.assertFalse(result)
            
            # Verify Query checked last 24h
            self.assertIn("datetime('now', '-1 day')", mock_cursor.execute.call_args[0][0])
            
        self.patcher_notify.start() # Re-patch for teardown consistency

if __name__ == '__main__':
    unittest.main()
