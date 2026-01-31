import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import sqlite3
import os

DB_PATH = "martian.db"

def setup_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    # Create tables (Simulate init_db)
    conn.execute("CREATE TABLE users (id TEXT PRIMARY KEY, is_initialized BOOLEAN DEFAULT 0, subscription_tier INTEGER DEFAULT 0)")
    conn.execute("CREATE TABLE user_groups (id TEXT PRIMARY KEY, user_id TEXT, name TEXT, created_at TEXT)")
    conn.commit()
    conn.close()

def list_groups_simulated(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check is_initialized
    cursor.execute("SELECT is_initialized FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    is_init = row[0] if row else 0
    print(f"User {user_id} is_initialized: {is_init}")
    
    # Check groups
    cursor.execute("SELECT * FROM user_groups WHERE user_id = ?", (user_id,))
    groups = cursor.fetchall()
    
    if not is_init:
        if not groups:
            print("Case 1: Creating Default...")
            # Simulate create default
            cursor.execute("INSERT INTO user_groups (id, user_id, name) VALUES ('g1', ?, 'Default')", (user_id,))
            cursor.execute("UPDATE users SET is_initialized = 1 WHERE id = ?", (user_id,))
            conn.commit()
            return ["Default"]
        else:
            print("Case 2: Self-Healing...")
            cursor.execute("UPDATE users SET is_initialized = 1 WHERE id = ?", (user_id,))
            conn.commit()
            return groups
    
    return groups

def run_test():
    setup_db()
    
    user_id = "test_user"
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    
    print("\n--- Test 1: New User ---")
    list_groups_simulated(user_id) # Should create default
    
    # Check flag
    conn = sqlite3.connect(DB_PATH)
    is_init = conn.execute("SELECT is_initialized FROM users WHERE id=?", (user_id,)).fetchone()[0]
    print(f"Flag after Test 1: {is_init}")
    assert is_init == 1
    
    # Delete groups
    conn.execute("DELETE FROM user_groups WHERE user_id=?", (user_id,))
    conn.commit()
    
    print("\n--- Test 2: Deleted Groups (Should NOT recreate) ---")
    res = list_groups_simulated(user_id)
    print(f"Groups: {res}")
    assert len(res) == 0 # Should be empty
    
    # Reset for Test 3 (Simulate Existing User with Groups but Flag=0)
    conn.execute("UPDATE users SET is_initialized = 0 WHERE id=?", (user_id,))
    conn.execute("INSERT INTO user_groups (id, user_id, name) VALUES ('g2', ?, 'My Group')", (user_id,))
    conn.commit()
    
    print("\n--- Test 3: Existing User (Self-Healing) ---")
    list_groups_simulated(user_id) # Should Self-Heal
    
    # Check flag
    is_init = conn.execute("SELECT is_initialized FROM users WHERE id=?", (user_id,)).fetchone()[0]
    print(f"Flag after Test 3: {is_init}")
    assert is_init == 1
    
    print("\n✅ Verification Passed!")

if __name__ == "__main__":
    run_test()
