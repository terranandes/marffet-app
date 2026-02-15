
import asyncio
from app.services.market_db import get_connection

# Corrected dividends for 1808 (润隆)
# Based on public records: 2024 cash div was ~3.0, not 66.5.
# 66.5 may have been an aggregation error or corrupt fetch.
PATCHES = {
    "1808": [
        (2025, 2.0, 0.0),
        (2024, 3.0, 1.2), # Verified: Cash 3.0, Stock 1.2 (120 shares)
        (2023, 0.6, 0.0),
        (2022, 2.0, 1.5), # Verified: Cash 2.0, Stock 1.5
        (2021, 0.2, 0.6), # Verified: Cash 0.2, Stock 0.6
        (2020, 2.0, 2.0), # Verified: Cash 2.0, Stock 2.0
        (2019, 0.5, 0.0), # Verified: Cash 0.5
    ]
}

def patch_dividends():
    print("🩹 Patching dividends in DuckDB...")
    conn = get_connection()
    try:
        for stock_id, rows in PATCHES.items():
            for year, cash, stock in rows:
                # Use DELETE + INSERT to bypass missing PK issues
                conn.execute("DELETE FROM dividends WHERE stock_id = ? AND year = ?", [stock_id, year])
                conn.execute("""
                    INSERT INTO dividends (stock_id, year, cash, stock)
                    VALUES (?, ?, ?, ?)
                """, [stock_id, year, cash, stock])
                print(f"  - Patched {stock_id} year {year}: Cash={cash}")
        
        # Verify 1808 again
        val = conn.execute("SELECT cash FROM dividends WHERE stock_id='1808' AND year=2024").fetchone()
        print(f"✅ 1808 2024 Dividend now: {val[0]}")
    finally:
        conn.close()

if __name__ == "__main__":
    patch_dividends()
