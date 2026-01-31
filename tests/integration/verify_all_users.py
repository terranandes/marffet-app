import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


import sys
import os
import sqlite3
import pandas as pd

# Setup environment to import app modules
sys.path.append(os.getcwd())
os.environ["DB_PATH"] = "app/portfolio.db"

from app.portfolio_db import get_portfolio_race_data, get_db

conn = sqlite3.connect("app/portfolio.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("--- Verifying Race Data for ALL Users ---")

# Get users with transactions
c.execute("""
    SELECT distinct u.id, u.email, u.name
    FROM transactions t
    JOIN group_targets gt ON t.target_id = gt.id
    JOIN user_groups ug ON gt.group_id = ug.id
    JOIN users u ON ug.user_id = u.id
""")
users = c.fetchall()

for u in users:
    uid = u['id']
    email = u['email']
    print(f"\nUser: {email} (ID: {uid[:5]}...)")
    
    try:
        data = get_portfolio_race_data(uid)
        count = len(data)
        if count > 0:
            last_month = data[-1]['month']
            total_val = sum(x['value'] for x in data if x['month'] == last_month)
            print(f"  ✅ SUCCESS: {count} rows. Last Month: {last_month} (Val: {total_val:,.0f})")
            
            # Check for ETFs specifically to verify the fix
            etfs = [x for x in data if x['asset_type'] == 'etf' and x['month'] == last_month]
            if etfs:
                print(f"     ETFs found: {[e['id'] for e in etfs]}")
            else:
                print("     No ETFs in this portfolio.")
                
        else:
            print("  ❌ EMPTY DATA returned.")
            
    except Exception as e:
        print(f"  🔥 CRASH: {e}")

conn.close()
