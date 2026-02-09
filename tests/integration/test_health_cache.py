import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_health_cache_endpoint_empty():
    # Scenario 1: Cache Empty
    with patch('app.services.market_cache._PRICES_CACHE', {}):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/health/cache")
            
            assert response.status_code == 200
            data = response.json()
            assert data["ready"] is False
            assert data["years"] == 0

@pytest.mark.asyncio
async def test_health_cache_endpoint_loaded():
    # Scenario 2: Cache Loaded with 2 years
    fake_cache = {
        2025: {"some": "data"},
        2026: {"some": "data"}
    }
    
    # We must patch where it is IMPORTED or used.
    # In app/main.py, we do: import app.services.market_cache as mc
    # So patching app.services.market_cache._PRICES_CACHE should work.
    
    with patch('app.services.market_cache._PRICES_CACHE', fake_cache):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/health/cache")
            
            assert response.status_code == 200
            data = response.json()
            assert data["ready"] is True
            assert data["years"] == 2
            assert data["oldest"] == "2025"
            assert data["newest"] == "2026"
