import sqlite3
import os
import uuid
from app.portfolio_db import init_db, list_groups, delete_group, get_db, DB_PATH
from pathlib import Path

# Override DB path for testing
TEST_DB = "test_portfolio_fix.db"
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

# We need to monkeypatch the DB_PATH or context manager, but app.portfolio_db uses a global DB_PATH.
# Let's just mock sqlite3.connect? Or modify the global variable if possible.
# Actually, since we're running this as a script, we can just set the module variable before importing/using?
# But we already imported.
import app.portfolio_db
app.portfolio_db.DB_PATH = Path(TEST_DB)

def run_test():
    print("1. Initializing DB...")
    init_db()
    
    user_id = "test_user_123"
    
    # Create user manually
    with app.portfolio_db.get_db() as conn:
        conn.execute("INSERT INTO users (id, name, is_initialized) VALUES (?, ?, ?)", (user_id, "Test User", 0))
    
    print("2. Listing groups for new user (Should init default)...")
    groups = list_groups(user_id)
    print(f"   Groups found: {len(groups)}")
    
    if len(groups) != 3:
        print("❌ Failed: Should have 3 default groups")
        return
        
    print("3. Checking is_initialized flag...")
    with app.portfolio_db.get_db() as conn:
        row = conn.execute("SELECT is_initialized FROM users WHERE id = ?", (user_id,)).fetchone()
        is_init = row[0]
        print(f"   is_initialized: {is_init}")
        
    if is_init != 1:
        print("❌ Failed: User should be marked initialized")
        return

    print("4. Deleting all groups...")
    for g in groups:
        delete_group(g['id'])
        
    print("5. Listing groups again (Should stay empty)...")
    groups_after = list_groups(user_id)
    print(f"   Groups found: {len(groups_after)}")
    
    if len(groups_after) == 0:
        print("✅ Success: Portfolio remained empty!")
    else:
        print("❌ Failed: Portfolio re-initialized incorrectly")

    # Cleanup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

if __name__ == "__main__":
    run_test()
