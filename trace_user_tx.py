import sqlite3
import pandas as pd

DB_PATH = "app/portfolio.db"
TARGET_EMAIL = "terranfund@gmail.com"

def check_user_transactions():
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # 1. Get User ID
        user = pd.read_sql(f"SELECT id, email FROM users WHERE email='{TARGET_EMAIL}'", conn)
        if user.empty:
            print(f"User {TARGET_EMAIL} not found.")
            return
        
        user_id = user.iloc[0]['id']
        print(f"User Found: {user_id}")
        
        # 2. Get User Groups
        groups = pd.read_sql(f"SELECT id FROM user_groups WHERE user_id='{user_id}'", conn)
        if groups.empty:
            print("No groups found for user.")
            return
        
        group_ids = tuple(groups['id'].tolist())
        print(f"Groups: {group_ids}")
        
        # 3. Get Targets
        if len(group_ids) == 1:
            query = f"SELECT id FROM group_targets WHERE group_id='{group_ids[0]}'"
        else:
            query = f"SELECT id FROM group_targets WHERE group_id IN {group_ids}"
            
        targets = pd.read_sql(query, conn)
        if targets.empty:
            print("No targets found in groups.")
            return
            
        target_ids = tuple(targets['id'].tolist())
        print(f"Found {len(targets)} targets.")
        
        # 4. Get Transactions
        if len(target_ids) == 1:
            tx_query = f"SELECT * FROM transactions WHERE target_id='{target_ids[0]}'"
        else:
            tx_query = f"SELECT * FROM transactions WHERE target_id IN {target_ids}"
            
        transactions = pd.read_sql(tx_query, conn)
        print(f"Total Transactions for user: {len(transactions)}")
        if not transactions.empty:
            print(transactions.head())
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user_transactions()
