import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import sqlite3
import pandas as pd

DB_PATH = "app/portfolio.db"

def inspect_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        
        print("=== Tables ===")
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
        print(tables)
        
        print("\n=== Users & Transaction Counts ===")
        try:
            users = pd.read_sql("SELECT id, email, name FROM users", conn)
            print(f"Total Users: {len(users)}")
            
            for _, user in users.iterrows():
                tx_count = pd.read_sql(f"SELECT COUNT(*) as count FROM transactions WHERE user_id='{user['id']}'", conn)
                print(f"User: {user['email']} ({user['name']}) -> Transactions: {tx_count['count'][0]}")
                
        except Exception as e:
            print(f"Error reading users/transactions: {e}")

        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = sys.argv[1]
        try:
            conn = sqlite3.connect(DB_PATH)
            print(f"Executing: {query}")
            df = pd.read_sql(query, conn)
            print(df.to_string())
            conn.close()
        except Exception as e:
            print(f"Query failed: {e}")
    else:
        inspect_db()
