from app.services.market_data_provider import MarketDataProvider
from app.services.market_db import get_connection

def inspect_9958():
    stock_id = "9958"
    
    # 1. Check Name
    print(f"--- Info for {stock_id} ---")
    conn = get_connection(read_only=True)
    row = conn.execute("SELECT stock_id, MIN(date), MAX(date) FROM daily_prices WHERE stock_id = ? GROUP BY stock_id", [stock_id]).fetchone()
    if row:
        print(f"Price Range: {row[1]} to {row[2]}")
    else:
        print("No Price Data")
        
    name_row = conn.execute("SELECT name, market_type, industry FROM stocks WHERE stock_id = ?", [stock_id]).fetchone()
    if name_row:
        print(f"DB Name: {name_row[0]}, Market: {name_row[1]}, Industry: {name_row[2]}")
    else:
        print("Stock not found in 'stocks' table")
    conn.close()

    # 4. Check YFinance Actions
    import yfinance as yf
    print(f"\n--- YFinance Actions for {stock_id} ---")
    t = yf.Ticker(f"{stock_id}.TW") # Try TW
    actions = t.actions
    if not actions.empty:
        print(actions.tail(10))
    else:
        print("No actions found for .TW")
        t = yf.Ticker(f"{stock_id}.TWO")
        print(t.actions.tail(10))

if __name__ == "__main__":
    inspect_9958()
