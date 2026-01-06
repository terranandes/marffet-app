import sys
import os
import sqlite3

# Add project root
sys.path.append(os.getcwd())

import app.portfolio_db
# Mock price fetch to avoid network block
app.portfolio_db.fetch_live_prices = lambda ids: {sid: {'price': 600.0} for sid in ids}

import app.portfolio_db
# Mock price fetch to avoid network block
app.portfolio_db.fetch_live_prices = lambda ids: {sid: {'price': 600.0} for sid in ids}

from app.portfolio_db import get_db, init_db, update_user_stats, get_leaderboard, get_public_portfolio

TEST_USER_ID = "test_social_bot_001"
TEST_STOCK_ID = "2330" # TSMC

def setup_test_data():
    print("🛠️ Setting up test data...")
    init_db()  # Ensure tables exist
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Create User
        cursor.execute("INSERT OR REPLACE INTO users (id, name, email, nickname, picture, last_synced) VALUES (?, ?, ?, ?, ?, ?)",
                      (TEST_USER_ID, "Test Bot", "bot@test.com", "SocialBot", "https://robohash.org/bot", None))
        
        # 2. Create Group
        cursor.execute("INSERT OR REPLACE INTO user_groups (id, user_id, name) VALUES (?, ?, ?)",
                      ("group_test_001", TEST_USER_ID, "Test Portfolio"))
        
        # 3. Create Target
        cursor.execute("INSERT OR REPLACE INTO group_targets (id, group_id, stock_id, stock_name, asset_type) VALUES (?, ?, ?, ?, ?)",
                      ("target_test_001", "group_test_001", TEST_STOCK_ID, "TSMC", "stock"))
                      
        # 4. Create Transaction (Buy)
        cursor.execute("DELETE FROM transactions WHERE target_id = ?", ("target_test_001",))
        cursor.execute("""
            INSERT INTO transactions (id, target_id, type, date, shares, price, fees, currency, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("tx_test_001", "target_test_001", "buy", "2020-01-01", 1000, 500.0, 0, "TWD", "Initial Buy"))
        
        conn.commit()

# ...

def cleanup():
    print("🧹 Cleanup...")
    with get_db() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (TEST_USER_ID,))
        conn.execute("DELETE FROM user_groups WHERE user_id = ?", (TEST_USER_ID,))
        conn.execute("DELETE FROM group_targets WHERE id = ?", ("target_test_001",))
        conn.execute("DELETE FROM transactions WHERE target_id = ?", ("target_test_001",))
    print("✅ Done.")

if __name__ == "__main__":
    try:
        setup_test_data()
        verify_logic()
    finally:
        cleanup()
