
import asyncio
import pandas as pd
from app.services.strategy_service import MarsStrategy, CBStrategy

# Mock Classes Manually to avoid Patching Issues
class MockCrawler:
    async def fetch_ex_rights_history(self, year):
        return {
            '1101': {'cash': 1.0, 'stock': 0.0}
        }
    
    async def fetch_issuance_data(self):
        return [
            {'IssuerCode': '1101', 'Conversion/ExchangePriceAtIssuance': '50', 'ShortName': 'TestCB', 'BondCode': '11011'}
        ]
    
    async def get_market_data(self, cb_code, stock_code):
        # Return cb_price=105, stock_price=52, success=True
        return 105.0, 52.0, True

class MockCalculator:
    def calculate_complex_simulation(self, df, start_year, dividend_data=None, stock_code="", buy_logic='FIRST_CLOSE'):
        return {
            'cagr_pct': 15.0,
            'volatility_pct': 5.0,
            'stock_code': stock_code,
            's2020e2021bao': 15.0,
            'cagr_std': 2.0,
            'valid_lasting_years': 2,
            'price': 100.0,
            'start_year': start_year
        }

# Patched Strategy Class
class TestMarsStrategy(MarsStrategy):
    def __init__(self):
        self.top_50 = []
        # Inject Mocks
        self.crawler = MockCrawler()
        self.calculator = MockCalculator()
        self.data_dir = "data/raw"

class TestCBStrategy(CBStrategy):
    def __init__(self):
        # Inject Mocks
        self.crawler = MockCrawler()
        self.issuance_data = []

async def test_logic():
    print("Testing MarsStrategy Logic...")
    mars = TestMarsStrategy()
    
    # We need to mock MarketCache.get_stock_history_fast
    # Since it's a static method on MarketCache class used inside analyze...
    # We can't easily replace it without patch unless we monkeypatch the module.
    # Monkeypatch app.services.strategy_service.MarketCache
    import app.services.strategy_service
    
    original_mc = app.services.strategy_service.MarketCache
    
    class MockMarketCache:
        @staticmethod
        def get_stock_history_fast(stock_id):
            return [
                {'year': 2020, 'close': 100, 'open': 90},
                {'year': 2021, 'close': 110, 'open': 100}
            ]
        @staticmethod
        def get_prices_db():
            return {2020: {'1101': {}}}
            
    app.services.strategy_service.MarketCache = MockMarketCache
    
    try:
        results = await mars.analyze(['1101'], start_year=2020)
        assert len(results) == 1
        assert results[0]['cagr_pct'] == 15.0
        print("MarsStrategy Analyze: PASS")
        
        # Test Export
        excel = mars.export_to_excel(results)
        assert len(excel) > 0
        print("MarsStrategy Export: PASS")
        
    finally:
        # Restore
        app.services.strategy_service.MarketCache = original_mc

    print("Testing CBStrategy Logic...")
    cb = TestCBStrategy()
    # Need to verify analyze logic
    # It calls MarketCache.get_stock_history_fast too.
    app.services.strategy_service.MarketCache = MockMarketCache
    try:
        results_cb = await cb.analyze(['1101'])
        # Expect 11011..11015 candidates.
        # MockCrawler.get_market_data returns valid for all.
        # MockCrawler.fetch_issuance_data returns 1 record for 1101.
        # Logic matches 1101 to 1101.
        
        # Wait, CBStrategy.analyze checks "11011" in candidates.
        # get_market_data returns valid.
        # Issuance data matches '1101' IssuerCode.
        # So it should calculate Premium.
        
        assert len(results_cb) > 0
        print(f"CBStrategy Results: {len(results_cb)}")
        print("CBStrategy Analyze: PASS")
    finally:
         app.services.strategy_service.MarketCache = original_mc

if __name__ == "__main__":
    asyncio.run(test_logic())
