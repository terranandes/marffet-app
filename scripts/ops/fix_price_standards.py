
import asyncio
import yfinance as yf
import pandas as pd
from app.services.market_db import get_connection
from datetime import datetime

# Priority stocks known to have "Adjusted" price junk in DuckDB
TARGET_STOCKS = ["1808", "2542", "2539", "3056", "2330", "0050"]

async def fix_price_standard(stock_id: str):
    print(f"🛠️  Fixing data standard for {stock_id}...")
    
    ticker_id = f"{stock_id}.TW"
    # standard download (auto_adjust=False) ensures NOMINAL prices
    data = yf.download(ticker_id, start="2000-01-01", auto_adjust=False, progress=False, threads=False)
    
    if data.empty:
        print(f"⚠️  No data found for {stock_id}")
        return

    # Flatten and format for market.duckdb
    data = data.reset_index()
    # Handle multi-index columns if present (new yfinance behavior)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]
    
    data['stock_id'] = stock_id
    data['market'] = 'TWSE'
    data['date'] = data['Date'].dt.date
    
    # Map columns to DuckDB schema (daily_prices)
    # Schema: stock_id, date, open, high, low, close, volume, market
    insert_data = []
    for _, row in data.iterrows():
        insert_data.append((
            stock_id,
            row['date'],
            float(row['Open']),
            float(row['High']),
            float(row['Low']),
            float(row['Close']),
            int(row['Volume']),
            'TWSE'
        ))

    conn = get_connection()
    try:
        # 1. Delete old data
        conn.execute("DELETE FROM daily_prices WHERE stock_id = ?", [stock_id])
        
        # 2. Insert fresh NOMINAL data
        conn.executemany("""
            INSERT INTO daily_prices (stock_id, date, open, high, low, close, volume, market)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, insert_data)
        
        print(f"✅ Replaced {len(insert_data)} rows for {stock_id} with NOMINAL prices.")
    finally:
        conn.close()

async def main():
    for stock in TARGET_STOCKS:
        await fix_price_standard(stock)
    print("\n🚀 All targeted stocks standardized to NOMINAL.")

if __name__ == "__main__":
    asyncio.run(main())
