import os
import pytest
import duckdb
from pathlib import Path
from app.services.market_db import init_schema, get_connection
import app.services.market_db as market_db

@pytest.fixture
def temp_db(tmp_path):
    """
    Fixture to provide a temporary database path.
    """
    db_file = tmp_path / "test_market.duckdb"
    original_path = market_db.DB_PATH
    market_db.DB_PATH = db_file
    yield db_file
    # Restore original path
    market_db.DB_PATH = original_path
    if db_file.exists():
        os.remove(db_file)

def test_init_schema(temp_db):
    """
    Test if init_schema correctly creates the tables.
    """
    init_schema()
    
    conn = get_connection(read_only=True)
    
    # Check tables
    tables = conn.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]
    
    assert "daily_prices" in table_names
    assert "dividends" in table_names
    assert "stocks" in table_names
    
    # Check daily_prices columns
    cols = conn.execute("DESCRIBE daily_prices").fetchall()
    col_names = [c[0] for c in cols]
    assert "stock_id" in col_names
    assert "date" in col_names
    assert "close" in col_names
    
    conn.close()

def test_idempotent_init(temp_db):
    """
    Test calling init_schema multiple times doesn't error.
    """
    init_schema()
    init_schema() # Should not raise
    
    conn = get_connection(read_only=True)
    tables = conn.execute("SHOW TABLES").fetchall()
    assert len(tables) == 3
    conn.close()
