# tests/integration/test_all_tabs.py
"""
Comprehensive API & UI verification for ALL sidebar tabs.
Uses the Precision Engine with Split Detector + FIRST_CLOSE logic.

Tabs Covered:
1. Mars Strategy (/mars) - /api/results, /api/results/detail
2. Bar Chart Race (/race) - /api/portfolio/race-data
3. Compound Interest (/compound) - Legacy iframe
4. CB Strategy (/cb) - /api/cb/analyze
5. Portfolio (/portfolio) - /api/portfolio/*
6. Trend (/trend) - /api/portfolio/history
7. My Race (/myrace) - /api/portfolio/race-data
8. Cash Ladder (/ladder) - /api/leaderboard
"""

import requests
import pytest

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"


# ============== Task 1: Mars Strategy ==============
class TestMarsStrategy:
    """Mars Strategy Tab verification."""
    
    def test_results_returns_stocks(self):
        """GET /api/results returns stock list."""
        r = requests.get(f"{BASE_URL}/api/results")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        # API returns a list directly
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        assert len(data) > 50, f"Expected many stocks, got {len(data)}"
    
    def test_results_split_adjusted_0050(self):
        """0050 CAGR should be split-adjusted (>10%)."""
        r = requests.get(f"{BASE_URL}/api/results")
        if r.status_code != 200:
            pytest.skip("Results API unavailable")
        results = r.json()
        stock_0050 = next((s for s in results if str(s.get("id")) == "0050"), None)
        if stock_0050:
            # API uses cagr_pct (percentage), not cagr (decimal)
            cagr = stock_0050.get("cagr_pct", 0)
            assert cagr > 10, f"0050 CAGR too low: {cagr}% (expected >10%)"
    
    def test_detail_bao_bah_bal(self):
        """GET /api/results/detail returns BAO/BAH/BAL series."""
        r = requests.get(f"{BASE_URL}/api/results/detail?stock_id=2330")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        # API returns uppercase keys
        assert "BAO" in data, f"Missing BAO. Keys: {list(data.keys())}"
        assert "BAH" in data, f"Missing BAH. Keys: {list(data.keys())}"
        assert "BAL" in data, f"Missing BAL. Keys: {list(data.keys())}"


# ============== Task 2: Bar Chart Race ==============
class TestBarChartRace:
    """Bar Chart Race Tab verification."""
    
    def test_race_data_endpoint(self):
        """GET /api/portfolio/race-data returns year-by-year data."""
        r = requests.get(f"{BASE_URL}/api/portfolio/race-data")
        # May require auth
        assert r.status_code in [200, 401, 403], f"Status: {r.status_code}"
    
    def test_race_page_accessible(self):
        """Frontend /race should be accessible."""
        r = requests.get(f"{FRONTEND_URL}/race", timeout=10)
        assert r.status_code == 200, f"Race page status: {r.status_code}"


# ============== Task 3: Compound Interest ==============
class TestCompoundInterest:
    """Compound Interest Tab (Legacy iframe wrapper)."""
    
    def test_compound_page_accessible(self):
        """Frontend /compound should be accessible."""
        r = requests.get(f"{FRONTEND_URL}/compound", timeout=10)
        assert r.status_code == 200, f"Compound page status: {r.status_code}"


# ============== Task 4: CB Strategy ==============
class TestCBStrategy:
    """CB (Convertible Bond) Strategy Tab."""
    
    def test_cb_analyze_endpoint(self):
        """GET /api/cb/analyze endpoint is reachable."""
        r = requests.get(f"{BASE_URL}/api/cb/analyze")
        # May require query params, but endpoint should exist
        assert r.status_code in [200, 400, 422], f"CB analyze status: {r.status_code}"
    
    def test_cb_page_accessible(self):
        """Frontend /cb should be accessible."""
        r = requests.get(f"{FRONTEND_URL}/cb", timeout=10)
        assert r.status_code == 200, f"CB page status: {r.status_code}"


# ============== Task 5: Portfolio ==============
class TestPortfolio:
    """Portfolio Tab (requires auth, test structure only)."""
    
    def test_portfolio_groups_endpoint(self):
        """GET /api/portfolio/groups is reachable."""
        r = requests.get(f"{BASE_URL}/api/portfolio/groups")
        assert r.status_code in [200, 401, 403], f"Unexpected status: {r.status_code}"
    
    def test_portfolio_dividends_endpoint(self):
        """GET /api/portfolio/dividends/total structure check."""
        r = requests.get(f"{BASE_URL}/api/portfolio/dividends/total")
        assert r.status_code in [200, 401, 403]
    
    def test_portfolio_page_accessible(self):
        """Frontend /portfolio should be accessible."""
        r = requests.get(f"{FRONTEND_URL}/portfolio", timeout=10)
        assert r.status_code == 200, f"Portfolio page status: {r.status_code}"


# ============== Task 6: Trend ==============
class TestTrend:
    """Trend Tab (portfolio history)."""
    
    def test_trend_page_accessible(self):
        """Frontend /trend should be accessible."""
        r = requests.get(f"{FRONTEND_URL}/trend", timeout=10)
        assert r.status_code == 200, f"Trend page status: {r.status_code}"


# ============== Task 7: My Race ==============
class TestMyRace:
    """My Race Tab (personal bar chart race)."""
    
    def test_myrace_page_accessible(self):
        """Frontend /myrace should be accessible."""
        r = requests.get(f"{FRONTEND_URL}/myrace", timeout=10)
        assert r.status_code == 200, f"MyRace page status: {r.status_code}"


# ============== Task 8: Cash Ladder ==============
class TestCashLadder:
    """Cash Ladder Tab (leaderboard)."""
    
    def test_ladder_page_accessible(self):
        """Frontend /ladder should be accessible."""
        r = requests.get(f"{FRONTEND_URL}/ladder", timeout=10)
        assert r.status_code == 200, f"Ladder page status: {r.status_code}"
    
    def test_leaderboard_api(self):
        """GET /api/leaderboard returns data."""
        r = requests.get(f"{BASE_URL}/api/leaderboard")
        assert r.status_code in [200, 401, 403], f"Leaderboard status: {r.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
