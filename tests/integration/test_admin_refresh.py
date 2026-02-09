import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from unittest.mock import patch

@pytest.mark.asyncio
async def test_admin_refresh_endpoint_success():
    from app.auth import get_admin_user
    
    # Override dependency to simulate admin user
    app.dependency_overrides[get_admin_user] = lambda: {"email": "gm@test.com", "is_admin": True}
    
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Mock MarketCache.get_prices_db
            with patch('app.services.market_cache.MarketCache.get_prices_db') as mock_get_db:
                 mock_get_db.return_value = {2000: {}, 2001: {}} # Mock return value
                 
                 response = await ac.post("/api/admin/refresh-market-data")
                 
                 assert response.status_code == 200
                 assert response.json() == {"status": "ok", "years_loaded": 2}
                 mock_get_db.assert_called_once_with(force_reload=True)
    finally:
        app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_admin_refresh_endpoint_fail_no_auth():
    # No dependency override implies no user session -> 401 or 403 depending on where it fails
    # Standard fail is 401 Authentication required or 403 Admin access required
    # Since we are not setting session, it should be 401
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/admin/refresh-market-data")
        # Just check it fails
        assert response.status_code in [401, 403]
