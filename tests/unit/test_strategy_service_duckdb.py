import pytest
from unittest.mock import MagicMock, patch
from app.services.strategy_service import MarsStrategy, CBStrategy
import pandas as pd
from datetime import datetime

@pytest.fixture
def mars_strategy():
    return MarsStrategy()

@pytest.fixture
def cb_strategy():
    return CBStrategy()

@pytest.mark.asyncio
async def test_mars_analyze_basic(mars_strategy):
    # Mock MarketDataProvider
    with patch("app.services.strategy_service.MarketDataProvider") as mock_mdp:
        # Mock get_stock_list
        mock_mdp.get_stock_list.return_value = ["2330"]
        
        # Mock get_daily_history
        mock_mdp.get_daily_history.return_value = [
            {"d": "2024-01-01", "o": 500.0, "h": 510.0, "l": 490.0, "c": 505.0, "v": 1000},
            {"d": "2024-12-31", "o": 600.0, "h": 610.0, "l": 590.0, "c": 605.0, "v": 1100}
        ]
        
        # Mock get_dividends
        mock_mdp.get_dividends.return_value = [
            {"year": 2024, "cash": 10.0, "stock": 0.0}
        ]
        
        results = await mars_strategy.analyze(["2330"], start_year=2024)
        
        assert len(results) > 0
        assert results[0]['stock_code'] == "2330"
        assert 'cagr_pct' in results[0]
        assert mock_mdp.get_daily_history.called
        assert mock_mdp.get_dividends.called

@pytest.mark.asyncio
async def test_cb_analyze_basic(cb_strategy):
    with patch("app.services.strategy_service.MarketDataProvider") as mock_mdp:
        with patch.object(CBStrategy, "initialize", return_value=None):
            cb_strategy.issuance_data = [{"IssuerCode": "2330", "Conversion/ExchangePriceAtIssuance": 500.0, "ShortName": "TSMC CB"}]
            
            mock_mdp.get_latest_price.return_value = 600.0
            
            # Mock CBCrawler.get_market_data
            with patch.object(cb_strategy.crawler, "get_market_data", return_value=(110.0, 0, True)):
                results = await cb_strategy.analyze(["2330"])
                
                assert len(results) > 0
                assert results[0]['stock_price'] == 600.0
                assert results[0]['cb_price'] == 110.0
