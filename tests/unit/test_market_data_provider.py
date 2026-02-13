import pytest
import os
from datetime import datetime
from app.services.market_data_provider import MarketDataProvider
from app.services.market_db import init_schema, get_connection
import app.services.market_db as market_db

@pytest.fixture
def temp_db(tmp_path):
    """
    Fixture to provide a temporary database path for tests.
    """
    db_file = tmp_path / "test_market_provider.duckdb"
    original_path = market_db.DB_PATH
    market_db.DB_PATH = db_file
    
    # Initialize schema
    init_schema()
    
    # Insert dummy data
    conn = get_connection()
    conn.execute("INSERT INTO stocks VALUES ('2330', 'TSMC', 'TWSE', 'Semicon')")
    conn.execute("INSERT INTO daily_prices VALUES ('2330', '2023-01-01', 500, 510, 490, 505, 1000, 'TWSE')")
    conn.execute("INSERT INTO daily_prices VALUES ('2330', '2023-01-02', 505, 520, 505, 515, 1200, 'TWSE')")
    conn.execute("INSERT INTO daily_prices VALUES ('2330', '2023-02-01', 515, 530, 510, 525, 800, 'TWSE')")
    conn.execute("INSERT INTO dividends VALUES ('2330', 2023, 11.0, 0.0)")
    conn.close()
    
    yield db_file
    
    # Clean up
    market_db.DB_PATH = original_path
    if db_file.exists():
        os.remove(db_file)

def test_get_daily_history(temp_db):
    history = MarketDataProvider.get_daily_history('2330')
    assert len(history) == 3
    assert history[0]['d'] == '2023-01-01'
    assert history[0]['c'] == 505

def test_get_latest_price(temp_db):
    # Reset cache for test isolation
    MarketDataProvider._latest_price_cache = {}
    
    price = MarketDataProvider.get_latest_price('2330')
    assert price == 525
    assert MarketDataProvider._latest_price_cache['2330'] == 525

def test_get_monthly_closes(temp_db):
    results = MarketDataProvider.get_monthly_closes(['2330'], 2023)
    assert '2330' in results
    # Monthly closes should have 2 points (one for Jan, one for Feb)
    # Jan 02 is the last day of Jan in our dummy data
    # Feb 01 is the last day of Feb in our dummy data
    assert len(results['2330']) == 2
    dates = [r['date'] for r in results['2330']]
    assert '2023-01-02' in dates
    assert '2023-02-01' in dates

def test_get_dividends(temp_db):
    divs = MarketDataProvider.get_dividends('2330')
    assert len(divs) == 1
    assert divs[0]['year'] == 2023
    assert divs[0]['cash'] == 11.0

def test_get_stock_list(temp_db):
    stocks = MarketDataProvider.get_stock_list()
    assert '2330' in stocks

def test_warm_latest_cache(temp_db):
    MarketDataProvider._latest_price_cache = {}
    MarketDataProvider.warm_latest_cache()
    assert '2330' in MarketDataProvider._latest_price_cache
    assert MarketDataProvider._latest_price_cache['2330'] == 525
