import sys
import duckdb
from app.services.market_db import get_connection

def purge_stock(stock_id):
    print(f"Purging data for stock {stock_id}...")
    conn = get_connection()
    try:
        # 1. Delete Daily Prices
        conn.execute("DELETE FROM daily_prices WHERE stock_id = ?", [stock_id])
        print(f"  Deleted daily_prices for {stock_id}")
        
        # 2. Delete Dividends
        conn.execute("DELETE FROM dividends WHERE stock_id = ?", [stock_id])
        print(f"  Deleted dividends for {stock_id}")
        
        # 3. Delete Stock Info (Optional, but safe to reload)
        # conn.execute("DELETE FROM stocks WHERE stock_id = ?", [stock_id])
        # print(f"  Deleted stocks entry for {stock_id}")
        
        print(f"Purge complete for {stock_id}")
    except Exception as e:
        print(f"Error purging {stock_id}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python purge_stock.py <stock_id>")
        sys.exit(1)
    purge_stock(sys.argv[1])
