
import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestMainRefactor:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_get_results_structure(self, client):
        """Verify /api/results returns correct structure after refactor (StrategyService)"""
        response = client.get("/api/results?start_year=2020&principal=1000000&contribution=60000")
        assert response.status_code == 200
        data = response.json()
        
        # Should be a list
        assert isinstance(data, list)
        
        if len(data) > 0:
            item = data[0]
            # Verify keys (StrategyService uses 'id')
            assert "id" in item
            assert "finalValue" in item # StrategyService aligns with Legacy UI (camelCase)
            assert "cagr_pct" in item

    def test_get_race_data_structure(self, client):
        """Verify /api/race-data returns correct structure (Legacy UI)"""
        response = client.get("/api/race-data?start_year=2020")
        assert response.status_code == 200
        data = response.json()
        
        # Should be a list
        assert isinstance(data, list)
        
        if len(data) > 0:
            item = data[0]
            # Key checks for race chart
            assert "year" in item # StrategyService uses 'year'
            assert "name" in item
            assert "value" in item
            assert "id" in item

    def test_get_results_detail(self, client):
        """Verify /api/results/detail works"""
        # 2330 TSMC is a safe bet to exist in history
        response = client.get("/api/results/detail?stock_id=2330&start_year=2015")
        assert response.status_code == 200
        data = response.json()
        
        # Check structure (Top level is BAO/BAH/BAL)
        assert "BAO" in data
        assert "BAH" in data
        assert "BAL" in data
        
        # Verify strict types in detail
        assert isinstance(data["BAO"], dict)
        assert "finalValue" in data["BAO"]

    def test_health_endpoints(self, client):
        """Verify health check passes"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
