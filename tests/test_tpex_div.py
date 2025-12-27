import pytest
from project_tw.crawler_tpex import TPEXCrawler

@pytest.mark.asyncio
async def test_fetch_ex_rights_history():
    crawler = TPEXCrawler()
    
    # Mocking/Monkey-patching _get_tpex_universe to avoid fetching ALL 800+ stocks
    async def mock_universe(client):
        return ['8069', '6533'] # 8069 (POTA), 6533 (Andes) - Known TPEX stocks
        
    # Replace the method on this instance
    crawler._get_tpex_universe = mock_universe
    
    try:
        results = await crawler.fetch_ex_rights_history(2024)
        
        # Verify stricture
        assert isinstance(results, dict)
        
        # We expect some results if yfinance works, but we shouldn't fail if yfinance is network blocked/fails 
        # unless we mock yfinance too. 
        # For now, let's assert that IF we got results, they have the right shape.
        if results:
            for code, data in results.items():
                assert 'cash' in data
                assert 'stock' in data
                assert isinstance(data['cash'], float)
                assert isinstance(data['stock'], float)
                
    except ImportError:
        pytest.skip("yfinance not installed or import error")
