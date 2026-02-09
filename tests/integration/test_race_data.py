
import pytest
from app.services import calculation_service 
from app.services.market_cache import MarketCache
from app.database import get_db, init_db
from app.repositories import user_repo, group_repo, target_repo, transaction_repo

def test_race_data_integration():
    """
    Test that get_portfolio_race_data works and uses MarketCache.
    """
    # 1. Setup DB
    init_db()
    user_id = "test_race_user"
    
    with get_db() as conn:
        # Clean up
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        user_repo.update_user_login(conn, user_id, "test@example.com", "Test User", "http://pic.com")
        
        # Create Portfolio
        group = group_repo.create_group(conn, user_id, "Test Group")
        target = target_repo.add_target(conn, group['id'], "2330", "TSMC")
        
        # Add Transaction
        transaction_repo.add_transaction(conn, target['id'], 'buy', 1000, 500.0, "2024-01-01")
        
    # 2. Ensure Cache is Populated (Lazy Load)
    # We can force a small subset or mock it, but integration test should use real files if present.
    # MarketCache loads from disk.
    db = MarketCache.get_prices_db()
    assert db is not None
    assert len(db) > 0, "MarketCache should load at least some years"
    
    # 3. Call Race Data
    race_data = calculation_service.get_portfolio_race_data(user_id)
    
    # 4. Assertions
    assert isinstance(race_data, list)
    # Check structure
    if race_data:
        first = race_data[0]
        assert "id" in first
        assert "value" in first
        assert "month" in first
        assert first['id'] == "2330"
        
    print(f"\nRace Data Rows: {len(race_data)}")
    
if __name__ == "__main__":
    test_race_data_integration()
