import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import sqlite3
import json

db_path = "app/portfolio.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

# Find target for 6533
cursor = conn.cursor()
cursor.execute("SELECT id, stock_id, stock_name FROM group_targets WHERE stock_id = '6533'")
targets = cursor.fetchall()
print(f"Targets for 6533: {len(targets)}")
for t in targets:
    print(f"  Target ID: {t['id']}, Stock: {t['stock_id']}, Name: {t['stock_name']}")
    
    # Get transactions for this target
    cursor.execute("SELECT id, type, shares, price, date FROM transactions WHERE target_id = ?", (t['id'],))
    txs = cursor.fetchall()
    print(f"  Transactions: {len(txs)}")
    for tx in txs:
        print(f"    {tx['date']} {tx['type'].upper()} {tx['shares']} @ ${tx['price']}")

conn.close()
