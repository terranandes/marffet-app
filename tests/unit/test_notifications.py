import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


import pytest
from unittest.mock import MagicMock, patch
from app.engines import RuthlessManager
from app import portfolio_db

# Mock Data
MOCK_USER_ID = "test_user"
MOCK_TARGET_ID = "t1"
MOCK_STOCK_ID = "2330"

@pytest.fixture
def mock_db_funcs():
    with patch('app.portfolio_db.get_all_targets_by_type') as mock_get_targets, \
         patch('app.portfolio_db.fetch_live_prices') as mock_prices, \
         patch('app.portfolio_db.create_notification') as mock_notify:
        
        yield {
            'get': mock_get_targets,
            'prices': mock_prices,
            'notify': mock_notify
        }

def test_gravity_alert_sell_euphoria(mock_db_funcs):
    """Test Gravity Alert: Price > 1.2 * SMA"""
    # Setup
    mock_db_funcs['get'].return_value = {
        'stock': [{'id': MOCK_TARGET_ID, 'stock_id': MOCK_STOCK_ID, 'stock_name': 'TSMC', 'total_shares': 1000}]
    }
    mock_db_funcs['prices'].return_value = {
        MOCK_STOCK_ID: {'price': 130} # Current Price
    }
    
    # Mock yfinance inside check_gravity_alert
    with patch('yfinance.Ticker') as MockTicker:
        # SMA = 100. 1.2 * 100 = 120. Price 130 > 120 -> ALERT
        instance = MockTicker.return_value
        instance.fast_info = {'lastPrice': 130, 'twoHundredDayAverage': 100}
        
        # Run
        RuthlessManager.run_checks(MOCK_USER_ID)
        
        # Verify
        mock_db_funcs['notify'].assert_called_with(
            MOCK_USER_ID, 'GRAVITY', 
            'Gravity Alert: TSMC Euphoria', 
            'Price (130) is > 20% above SMA250 (100). Sell the euphoria.', 
            target_id=MOCK_TARGET_ID
        )

def test_gravity_alert_buy_fear(mock_db_funcs):
    """Test Gravity Alert: Price < 0.8 * SMA"""
    mock_db_funcs['get'].return_value = {
        'stock': [{'id': MOCK_TARGET_ID, 'stock_id': MOCK_STOCK_ID, 'stock_name': 'TSMC', 'total_shares': 1000}]
    }
    mock_db_funcs['prices'].return_value = {
        MOCK_STOCK_ID: {'price': 70} 
    }
    
    with patch('yfinance.Ticker') as MockTicker:
        # SMA = 100. 0.8 * 100 = 80. Price 70 < 80 -> ALERT
        instance = MockTicker.return_value
        instance.fast_info = {'lastPrice': 70, 'twoHundredDayAverage': 100}
        
        RuthlessManager.run_checks(MOCK_USER_ID)
        
        mock_db_funcs['notify'].assert_called()
        assert "Fear" in mock_db_funcs['notify'].call_args[0][2]

def test_size_authority_overweight(mock_db_funcs):
    """Test Size Authority: Cap > 1.2 * Avg"""
    # 2 Targets. Avg Cap needs to be calculated.
    # T1: 1000 shares * $10 = $10,000
    # T2: 1000 shares * $50 = $50,000 (Giant)
    # Total = 60000. Avg = 30000. 
    # T2 is 50000. 1.2 * 30000 = 36000. 50k > 36k -> ALERT for T2.
    
    mock_db_funcs['get'].return_value = {
        'stock': [
            {'id': 't1', 'stock_id': '1101', 'stock_name': 'Cement', 'total_shares': 1000},
            {'id': 't2', 'stock_id': '2330', 'stock_name': 'TSMC', 'total_shares': 1000}
        ]
    }
    mock_db_funcs['prices'].return_value = {
        '1101': {'price': 10},
        '2330': {'price': 50}
    }
    
    # Disable Gravity Check for this test
    with patch.object(RuthlessManager, 'check_gravity_alert'):
        RuthlessManager.run_checks(MOCK_USER_ID)
        
        # Should call notify for T2 (Size Authority)
        calls = mock_db_funcs['notify'].call_args_list
        found = False
        for call in calls:
            if call[0][1] == 'SIZE' and 'Overweight' in call[0][2] and call[1]['target_id'] == 't2':
                found = True
        assert found

def test_cooldown_returns_false():
    """Verify create_notification returns False if duplicate exists"""
    # This requires mocking the DB connection cursor logic
    with patch('app.portfolio_db.get_db') as mock_ctx:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_ctx.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock COUNT(*) > 0 (Duplicate exists)
        mock_cursor.fetchone.return_value = [1] 
        
        result = portfolio_db.create_notification("u1", "GRAVITY", "Title", "Msg", "t1")
        assert result is False # Deduplicated
        
        # Verify Query checked last 24h
        assert "datetime('now', '-1 day')" in mock_cursor.execute.call_args[0][0]

