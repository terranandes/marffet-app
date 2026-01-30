import sqlite3
import pandas as pd

DB_PATH = "app/portfolio.db"

def inspect_schema():
    try:
        conn = sqlite3.connect(DB_PATH)
        print("=== Transactions Table Schema ===")
        schema = pd.read_sql("PRAGMA table_info(transactions)", conn)
        print(schema)
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    inspect_schema()
