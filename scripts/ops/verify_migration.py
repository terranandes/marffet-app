import duckdb
import os
import sys
from datetime import date

def verify_migration():
    if not os.path.exists('data/market.duckdb'):
        print("FAIL: data/market.duckdb not found")
        sys.exit(1)

    print("Verifying DuckDB Migration...")
    try:
        conn = duckdb.connect('data/market.duckdb', read_only=True)
        
        # 1. Row Counts
        prices = conn.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
        dividends = conn.execute("SELECT COUNT(*) FROM dividends").fetchone()[0]
        stocks = conn.execute("SELECT COUNT(*) FROM stocks").fetchone()[0]
        
        print(f"Prices:    {prices:,}")
        print(f"Dividends: {dividends:,}")
        print(f"Stocks:    {stocks:,}")
        
        if prices < 100000:
            print("WARNING: Price count seems low (<100k). Expected >1M for full history.")
        
        # 2. Historical Depth (TSMC 2330)
        tsmc_rows = conn.execute("SELECT COUNT(*) FROM daily_prices WHERE stock_id='2330'").fetchone()[0]
        print(f"TSMC Rows: {tsmc_rows}")
        
        min_date, max_date = conn.execute("SELECT MIN(date), MAX(date) FROM daily_prices WHERE stock_id='2330'").fetchone()
        print(f"TSMC Range: {min_date} to {max_date}")
        
        # Check if we have monthly granularity (Race Cache)
        # Count distinct months in 2010
        months_2010 = conn.execute("SELECT COUNT(DISTINCT MONTH(date)) FROM daily_prices WHERE stock_id='2330' AND YEAR(date)=2010").fetchone()[0]
        print(f"TSMC Months in 2010: {months_2010}")
        
        if months_2010 < 10:
             print("WARNING: TSMC 2010 data lacks monthly granularity (likely only yearly summary). Volatility calculation will fail.")
        else:
             print("SUCCESS: TSMC 2010 has monthly granularity.")

        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_migration()
