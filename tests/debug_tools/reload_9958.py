"""
Emergency reload for stock 9958 (世紀鋼) after purge.
crawl_fast.py batch mode failed, so we use individual yfinance fetch.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
from app.services.market_db import get_connection

STOCK_ID = "9958"
TICKER = f"{STOCK_ID}.TW"

def reload():
    print(f"=== Reloading {STOCK_ID} ({TICKER}) ===")
    
    # 1. Fetch Price History
    t = yf.Ticker(TICKER)
    hist = t.history(period="max", auto_adjust=False)
    
    if hist.empty:
        print("ERROR: No price data from yfinance!")
        return
    
    print(f"Fetched {len(hist)} price rows ({hist.index.min().date()} to {hist.index.max().date()})")
    
    # 2. Fetch Dividends & Splits
    actions = t.actions
    print(f"Fetched {len(actions)} action rows")
    if not actions.empty:
        print(actions)
    
    # 3. Insert Prices into DuckDB
    conn = get_connection()
    
    price_rows = []
    for dt_idx, row in hist.iterrows():
        dt = dt_idx.tz_localize(None) if dt_idx.tzinfo else dt_idx
        price_rows.append((
            STOCK_ID,
            dt.strftime("%Y-%m-%d"),
            float(row['Open']),
            float(row['High']),
            float(row['Low']),
            float(row['Close']),
            int(row['Volume']) if pd.notna(row['Volume']) else 0
        ))
    
    # Batch insert
    conn.executemany(
        "INSERT OR REPLACE INTO daily_prices (stock_id, date, open, high, low, close, volume) VALUES (?,?,?,?,?,?,?)",
        price_rows
    )
    print(f"Inserted {len(price_rows)} price rows into DuckDB")
    
    # 4. Insert Dividends
    # Group by year, sum cash dividends
    div_by_year = {}
    split_by_year = {}
    
    for dt_idx, row in actions.iterrows():
        dt = dt_idx.tz_localize(None) if dt_idx.tzinfo else dt_idx
        year = dt.year
        
        cash = float(row.get('Dividends', 0))
        split = float(row.get('Stock Splits', 0))
        
        if cash > 0:
            div_by_year[year] = div_by_year.get(year, 0) + cash
        if split > 0 and split != 1.0:
            split_by_year[year] = split_by_year.get(year, 0) + (split - 1) * 10
    
    # Insert dividends
    for year, cash in div_by_year.items():
        stock_div = split_by_year.get(year, 0.0)
        conn.execute(
            "INSERT OR REPLACE INTO dividends (stock_id, year, cash, stock) VALUES (?,?,?,?)",
            [STOCK_ID, year, cash, stock_div]
        )
        print(f"  Div {year}: cash={cash:.4f}, stock={stock_div:.4f}")
    
    conn.close()
    print(f"\n=== Reload complete for {STOCK_ID} ===")
    
    # 5. Verify
    conn2 = get_connection(read_only=True)
    count = conn2.execute("SELECT COUNT(*) FROM daily_prices WHERE stock_id = ?", [STOCK_ID]).fetchone()[0]
    div_count = conn2.execute("SELECT COUNT(*) FROM dividends WHERE stock_id = ?", [STOCK_ID]).fetchone()[0]
    print(f"Verification: {count} prices, {div_count} dividends in DuckDB")
    conn2.close()

if __name__ == "__main__":
    reload()
