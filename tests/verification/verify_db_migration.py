import sqlite3
import sys
import os

sys.path.append(os.getcwd())
from app.portfolio_db import get_db, init_db

def verify_migration():
    print("Initializing DB (triggering migrations)...")
    init_db()
    
    with get_db() as conn:
        cursor = conn.cursor()
        print("Checking users table schema...")
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Columns: {columns}")
        
        missing_cols = []
        for col in ['auth_provider', 'last_login_at', 'picture', 'subscription_tier']:
            if col not in columns:
                missing_cols.append(col)
        
        if not missing_cols:
            print("SUCCESS: All required columns found.")
        else:
            print(f"FAILURE: Missing columns: {missing_cols}")
            sys.exit(1)

if __name__ == "__main__":
    verify_migration()
