"""
TWSE Dividend Re-Import Script (Hybrid Approach)

Goal: Overwrite DuckDB 'dividends' table with nominal data to fix the adjusted-dividend double-counting bug.

Strategy:
1. Primary Source (2003-Present): TWSE TWT49U endpoint.
   - Handles '息' (Cash) and '權' (Stock) types correctly.
   - Ambiguous '權息' (Combined) types are logged for fallback.
2. Fallback Source:
   - For '權息' types: Uses a HARDCODED patch map for known outliers (1808, 2327, etc.) temporarily.
   - For Pre-2003: Uses a HARDCODED patch map for key stocks.
   - TODO: Integrate live Goodinfo scraper for full coverage.

Usage:
    python scripts/ops/reimport_twse_dividends.py [start_year] [end_year]
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.project_tw.crawler import TWSECrawler
from app.services.market_db import get_connection

# --- FALLBACK PATCH DATA (Source: Goodinfo/Public Data) ---
# Format: {stock_id: {year: {'cash': float, 'stock': float}}}
FALLBACK_PATCHES = {
    # 1808 (润隆) - Known Outlier with many Stock Dividends
    "1808": {
        2000: {'cash': 0.0, 'stock': 2.0},
        2001: {'cash': 0.5, 'stock': 1.0},
        2002: {'cash': 0.0, 'stock': 0.0}, 
        2024: {'cash': 3.0, 'stock': 1.2}, 
        2022: {'cash': 2.0, 'stock': 1.5},
        2021: {'cash': 0.2, 'stock': 0.6},
        2020: {'cash': 2.0, 'stock': 2.0},
        2015: {'cash': 0.5, 'stock': 0.0},
        2019: {'cash': 0.5, 'stock': 0.0},
        2018: {'cash': 0.5, 'stock': 0.0},
        2017: {'cash': 0.5, 'stock': 0.0},
        2011: {'cash': 0.5, 'stock': 0.0}
    },
    # 4763 (材料*-KY) - Fix 100x Inflation from Combined Type
    "4763": {
        2024: {'cash': 26.0, 'stock': 0.0}, # H1 2024
        2023: {'cash': 31.5, 'stock': 4.0}, # 152 in DuckDB previously
    },
    # 1519 (華城) - Fix Combined Type Inflation
    "1519": {
        2024: {'cash': 7.0, 'stock': 0.0},  # Price ~800, Div was ~90
        2023: {'cash': 2.5, 'stock': 0.5},
    },
    # 8070 (長華*) - Fix Combined Type Inflation
    "8070": {
        2024: {'cash': 1.23, 'stock': 0.0}, 
        2023: {'cash': 2.1, 'stock': 0.0},
        2021: {'cash': 3.0, 'stock': 0.0},
    },
    # 2330 (TSMC) - Fix TWT49U Derivation Overshoot
    "2330": {
        2009: {'cash': 3.0, 'stock': 0.05},
        2008: {'cash': 3.0, 'stock': 0.05},
        2007: {'cash': 3.0, 'stock': 0.05},
        2006: {'cash': 2.5, 'stock': 0.3},
    },
    # 2327 (國巨)
    "2327": {
         2018: {'cash': 15.0, 'stock': 0.0},
         2019: {'cash': 45.0, 'stock': 0.0},
    },
    # 2542 (興富發)
    "2542": {
         2014: {'cash': 2.0, 'stock': 5.0}, # Ref Price jump was 25.7
    }
}

async def reimport_dividends(start_year: int = 2003, end_year: int = 2025):
    """Re-crawl TWSE TWT49U and overwrite DuckDB dividends table."""
    crawler = TWSECrawler(data_dir="data/raw_dividends")
    conn = get_connection()
    
    # Efficiently fetch prices for yield checking (bulk)
    print("📈 Pre-fetching prices for yield sanity checks...")
    all_prices = conn.execute("SELECT stock_id, year(date) as year, AVG(close) as avg_price FROM daily_prices GROUP BY stock_id, year").df()
    price_map = all_prices.set_index(['stock_id', 'year'])['avg_price'].to_dict()

    # 1. Backup Stats
    existing_count = conn.execute("SELECT COUNT(*) FROM dividends").fetchone()[0]
    print(f"📊 Existing DuckDB dividend records: {existing_count}")
    
    # 2. Clear Table
    print("🗑️  Clearing existing (adjusted) dividend data...")
    conn.execute("DELETE FROM dividends")
    
    total_inserted = 0
    skipped_outliers = 0
    
    # 3. Crawl Loop
    for year in range(start_year, end_year + 1):
        print(f"\n📅 Fetching TWSE dividends for {year}...")
        try:
            div_data = await crawler.fetch_ex_rights_history(year)
            
            if not div_data:
                print(f"  ⚠️  No dividend data for {year}")
                continue
                
            # Step B: Insert with Patch Overlay
            rows_to_insert = []
            
            for stock_id, vals in div_data.items():
                cash = float(vals.get('cash', 0.0))
                stock = float(vals.get('stock', 0.0))
                
                # Apply Patch
                if stock_id in FALLBACK_PATCHES and year in FALLBACK_PATCHES[stock_id]:
                    patch = FALLBACK_PATCHES[stock_id][year]
                    cash = patch.get('cash', cash)
                    stock = patch.get('stock', stock)
                else:
                    # SYSTEMIC SANITY CHECK (Protect against parser inflation)
                    # If yield > 30%, it's almost certainly a 'Combined' parser error we missed.
                    avg_p = price_map.get((stock_id, year))
                    if avg_p and cash > 0:
                        yield_pct = (cash / avg_p) * 100
                        if yield_pct > 30.0:
                            print(f"  ❗ Skip Outlier {stock_id} in {year}: Yield {yield_pct:.1f}% (Cash={cash}, Price={avg_p:.1f})")
                            cash = 0.0
                            skipped_outliers += 1

                if cash > 0 or stock > 0:
                    rows_to_insert.append((stock_id, year, cash, stock))
            
            if rows_to_insert:
                conn.executemany(
                    "INSERT INTO dividends (stock_id, year, cash, stock) VALUES (?, ?, ?, ?)",
                    rows_to_insert
                )
                total_inserted += len(rows_to_insert)
                print(f"  ✅ Inserted {len(rows_to_insert)} records for {year}")
            else:
                print(f"  ⚠️  No valid dividend records for {year}")
                
        except Exception as e:
            print(f"  ❌ Error for {year}: {e}")
            import traceback
            traceback.print_exc()

    # 4. Insert Pre-2003 Patches (If any)
    print("\n📦 Inserting Pre-2003 Fallback Data...")
    pre_2003_rows = []
    for stock_id, year_map in FALLBACK_PATCHES.items():
        for year, vals in year_map.items():
            if year < start_year: # Insert if outside crawl range
                pre_2003_rows.append((stock_id, year, vals['cash'], vals['stock']))
                
    if pre_2003_rows:
        conn.executemany(
            "INSERT INTO dividends (stock_id, year, cash, stock) VALUES (?, ?, ?, ?)",
            pre_2003_rows
        )
        print(f"  ✅ Inserted {len(pre_2003_rows)} pre-2003 records")
        total_inserted += len(pre_2003_rows)

    # 5. Final Verification
    new_count = conn.execute("SELECT COUNT(*) FROM dividends").fetchone()[0]
    print(f"\n{'='*60}")
    print(f"📊 Migration Complete!")
    print(f"   Before: {existing_count}")
    print(f"   After:  {new_count}")
    print(f"   Total Inserted: {total_inserted}")
    
    # Spot Check 1808
    print(f"\n🔍 Spot Check - 1808 (润隆):")
    rows = conn.execute("SELECT year, cash, stock FROM dividends WHERE stock_id='1808' ORDER BY year").fetchall()
    for r in rows:
        print(f"   {r[0]}: cash={r[1]:.2f}, stock={r[2]:.2f}")
        
    conn.close()

if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 2003
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 2025
    asyncio.run(reimport_dividends(start, end))
