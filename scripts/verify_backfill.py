import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = Path('data/market.duckdb')

def verify_backfill():
    print(f"Connecting to {DB_PATH}...")
    try:
        conn = duckdb.connect(str(DB_PATH), read_only=True)
    except Exception as e:
        print(f"Error connecting: {e}")
        return

    print("\n--- 2000-2004 Integrity Check ---")
    
    # 1. Total Rows
    total_rows = conn.execute("SELECT count(*) FROM daily_prices WHERE date BETWEEN '2000-01-01' AND '2004-12-31'").fetchone()[0]
    print(f"Total Price Rows (2000-2004): {total_rows}")

    # 2. Distinct Stocks
    stocks = conn.execute("SELECT distinct stock_id FROM daily_prices WHERE date BETWEEN '2000-01-01' AND '2004-12-31' ORDER BY stock_id").fetchall()
    stocks = [s[0] for s in stocks]
    print(f"Distinct Stocks with Data: {len(stocks)}")

    # 3. Year Coverage per Stock
    print("\n--- Coverage Analysis (Top 10) ---")
    coverage_df = conn.execute("""
        SELECT stock_id, 
               min(date) as start_date, 
               max(date) as end_date,
               count(*) as distinct_days,
               count(distinct year(date)) as distinct_years
        FROM daily_prices 
        WHERE date BETWEEN '2000-01-01' AND '2004-12-31'
        GROUP BY stock_id
        ORDER BY distinct_days DESC
        LIMIT 10
    """).df()
    print(coverage_df)

    # 4. Dividend Check
    div_rows = conn.execute("SELECT count(*) FROM dividends WHERE year BETWEEN 2000 AND 2004").fetchone()[0]
    print(f"\nTotal Dividend Records (2000-2004): {div_rows}")
    
    # 5. Check for Stocks with Prices but NO Dividends (Sample)
    # Most stocks pay dividends. If huge mismatch, potential issue.
    stocks_with_divs = conn.execute("SELECT count(distinct stock_id) FROM dividends WHERE year BETWEEN 2000 AND 2004").fetchone()[0]
    print(f"Distinct Stocks with Dividends: {stocks_with_divs}")
    
    # 6. Check for Broken Gaps (e.g. 2000, 2002 exists, 2001 missing)
    # Logic: For each stock, if (max_year - min_year + 1) != distinct_years?
    print("\n--- Gap Analysis ---")
    gaps = conn.execute("""
        WITH Years AS (
            SELECT stock_id, year(date) as y
            FROM daily_prices
            WHERE date BETWEEN '2000-01-01' AND '2004-12-31'
            GROUP BY stock_id, y
        ),
        Stats AS (
            SELECT stock_id, min(y) as min_y, max(y) as max_y, count(*) as cnt
            FROM Years
            GROUP BY stock_id
        )
        SELECT stock_id, min_y, max_y, cnt
        FROM Stats
        WHERE (max_y - min_y + 1) != cnt
    """).df()
    
    if not gaps.empty:
        print(f"Found {len(gaps)} stocks with year gaps!")
        print(gaps.head())
    else:
        print("No year gaps found for any stock!")

if __name__ == "__main__":
    verify_backfill()
