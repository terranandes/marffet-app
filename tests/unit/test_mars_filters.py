import pytest
from unittest.mock import MagicMock, patch
from app.services.strategy_service import MarsStrategy

@pytest.fixture
def strategy():
    return MarsStrategy()

def test_mars_filters(strategy):
    # Mock data representing processed results
    # 2330: TSMC (Baseline)
    # A: Good Stock
    # B: Inactive (End Year 2020)
    # C: Short History (3 years)
    # D: High Volatility (4x TSMC)
    # E: ETF (Ends with L)
    # F: Unstable (CAGR Std > 20)
    
    current_year = 2026
    
    mock_results = [
        # TSMC (Baseline) - Volatility 20%
        {'stock_code': '2330', 'valid_lasting_years': 20, 'cagr_std': 5.0, 'volatility_pct': 20.0, 'end_year': current_year, 'finalValue': 100},
        
        # Stock A (Good) - Volatility 30% (< 60%), Active, Stable
        {'stock_code': '1101', 'valid_lasting_years': 20, 'cagr_std': 10.0, 'volatility_pct': 30.0, 'end_year': current_year, 'finalValue': 200},
        
        # Stock B (Inactive) - Ends 2020
        {'stock_code': '9999', 'valid_lasting_years': 20, 'cagr_std': 5.0, 'volatility_pct': 20.0, 'end_year': 2020, 'finalValue': 100},
        
        # Stock C (Short) - 3 Years
        {'stock_code': '8888', 'valid_lasting_years': 3, 'cagr_std': 5.0, 'volatility_pct': 20.0, 'end_year': current_year, 'finalValue': 100},
        
        # Stock D (Volatile) - Volatility 80% (> 3*20=60%)
        {'stock_code': '7777', 'valid_lasting_years': 20, 'cagr_std': 5.0, 'volatility_pct': 80.0, 'end_year': current_year, 'finalValue': 100},
        
        # Stock E (ETF) - Ends with L
        {'stock_code': '0050L', 'valid_lasting_years': 20, 'cagr_std': 5.0, 'volatility_pct': 20.0, 'end_year': current_year, 'finalValue': 100},
        
        # Stock F (Unstable) - CAGR Std 25 (> 20)
        {'stock_code': '6666', 'valid_lasting_years': 20, 'cagr_std': 25.0, 'volatility_pct': 20.0, 'end_year': current_year, 'finalValue': 100},
    ]
    
    # We need to inject this into analyze or test a helper method.
    # Since analyze is complex to mock fully (DB calls), let's extract the filter logic to checking it.
    # But for now, let's assume we add a method `_apply_filters(results)` to MarsStrategy.
    # We will test that method.
    
    # Monkey patch the method if it doesn't exist yet (TBD in implementation)
    # For TDD, we assume strat has `apply_filters`.
    
    if not hasattr(strategy, 'apply_filters'):
        pytest.fail("MarsStrategy.apply_filters method not found. Implement it first or adjust test.")
    
    filtered = strategy.apply_filters(mock_results)
    
    # Assertions
    codes = [r['stock_code'] for r in filtered]
    
    assert '2330' in codes, "TSMC should remain"
    assert '1101' in codes, "Stock A should remain"
    assert '9999' not in codes, "Inactive stock should be removed"
    assert '8888' not in codes, "Short history stock should be removed"
    assert '7777' not in codes, "High volatility stock should be removed"
    assert '0050L' not in codes, "Leveraged ETF should be removed"
    assert '6666' not in codes, "Unstable stock should be removed"
    
    assert len(filtered) == 2
