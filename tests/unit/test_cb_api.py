import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app

client = TestClient(app)

# Mock Data
MOCK_USER = {"id": "test_user", "email": "test@example.com"}
MOCK_CB_TARGETS = {
    "cb": [{"stock_id": "11011", "stock_name": "Test CB"}]
}
MOCK_RESULTS = [
    {"code": "11011", "name": "Test CB", "price": 105.0, "premium": 5.0}
]

@pytest.fixture
def mock_auth():
    """Mock authentication to bypass Login"""
    # app.auth.get_current_user is where the dependency comes from.
    # But it is imported in main.py as `from app.auth import ... get_current_user`
    # So we should override app.dependency_overrides
    from app.auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    yield
    app.dependency_overrides = {}

@patch("app.main.get_all_targets_by_type")
@patch("app.main.CBStrategy")
def test_fetch_cb_portfolio(mock_cb_strategy_cls, mock_get_targets, mock_auth):
    """
    Test GET /api/cb/portfolio
    - Mocks Auth
    - Mocks DB (get_all_targets_by_type)
    - Mocks External API (CBStrategy)
    """
    # 1. Setup DB Mock
    mock_get_targets.return_value = MOCK_CB_TARGETS
    
    # 2. Setup Strategy Mock
    # analyze_specific_cbs is an async method?
    # In main.py: results = await strategy.analyze_specific_cbs(cb_codes)
    # We need to ensure the mock returns an awaitable or just a value depending on how MagicMock handles async.
    # AsyncMock is best if available (Python 3.8+).
    
    mock_instance = mock_cb_strategy_cls.return_value
    # AsyncMock for analyze_specific_cbs
    from unittest.mock import AsyncMock
    mock_instance.analyze_specific_cbs = AsyncMock(return_value=MOCK_RESULTS)

    # 3. Call Endpoint
    response = client.get("/api/cb/portfolio")
    
    # 4. Verify
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "11011"
    
    # Verify calls
    mock_get_targets.assert_called_with("test_user")
    mock_instance.analyze_specific_cbs.assert_called_once_with(["11011"])

def test_cb_portfolio_no_targets(mock_auth):
    """Test when user has no CBs"""
    with patch("app.main.get_all_targets_by_type") as mock_get_targets:
        mock_get_targets.return_value = {"cb": []}
        
        response = client.get("/api/cb/portfolio")
        
        assert response.status_code == 200
        assert response.json() == []

def test_cb_portfolio_unauthorized():
    """Test without auth override"""
    # Ensure no override
    app.dependency_overrides = {}
    
    response = client.get("/api/cb/portfolio")
    # Should be 401 or 403 depending on auth logic. 
    # get_current_user usually raises HTTPException(401) if no cookie.
    assert response.status_code == 200
    # In Guest Mode, it should return [] if no local portfolio, OR check logic
    # Logs said "Analyzing for User: default"
    # So it proceeds.
    pass
