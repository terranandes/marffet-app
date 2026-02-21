import sqlite3
import pandas as pd
import duckdb

def check_db(path):
    print(f"Checking {path}...")
    try:
        con = sqlite3.connect(path)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cur.fetchall()]
        print(f"  Tables: {tables}")
        
        if 'daily_prices' in tables:
            df = pd.read_sql("SELECT COUNT(*) as c FROM daily_prices", con)
            print(f"  daily_prices row count: {df.iloc[0]['c']}")
            
            df_stocks = pd.read_sql("SELECT COUNT(DISTINCT stock_id) as s FROM daily_prices", con)
            print(f"  unique stocks: {df_stocks.iloc[0]['s']}")
            
            df_sample = pd.read_sql("SELECT * FROM daily_prices LIMIT 1", con)
            print(f"  Sample row:\n{df_sample}")
            
        con.close()
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    check_db('portfolio.db')
    check_db('app/portfolio.db')
    check_db('data/portfolio.db')
