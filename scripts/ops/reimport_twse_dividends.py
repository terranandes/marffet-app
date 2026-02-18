"""
TWSE Dividend Re-Import Script (Hybrid Approach)

Goal: Overwrite DuckDB 'dividends' table with nominal data to fix the adjusted-dividend double-counting bug.

Strategy:
1. Primary Source (2003-Present): TWSE TWT49U endpoint (via cache).
   - Standard rows: Used as is.
   - Combined rows ('權息'): Initially just Total Value (Cash).
2. Patch Source (Goodinfo Static Reference):
   - `data/ref/goodinfo_dividends.json` contains exact Cash/Stock splits for combined rows.
   - Overwrites TWT49U data if a match is found.

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

# --- PATCH DATA (Source: Goodinfo/Public Data) ---
PATCH_FILE = "data/ref/goodinfo_dividends.json"
PATCH_DATA = {}

if os.path.exists(PATCH_FILE):
    try:
        with open(PATCH_FILE, 'r') as f:
            PATCH_DATA = json.load(f)
        print(f"📦 Loaded {len(PATCH_DATA)} stocks from patch file: {PATCH_FILE}")
    except Exception as e:
        print(f"⚠️ Error loading patch file: {e}")
else:
    print(f"⚠️ Patch file not found: {PATCH_FILE} (Running without patches)")

# --- KY/DR PATCH DATA (Source: YFinance) ---
KY_PATCH_FILE = "data/ref/ky_dividend_patch.json"
KY_PATCH_DATA = {}
if os.path.exists(KY_PATCH_FILE):
    try:
        with open(KY_PATCH_FILE, 'r') as f:
            KY_PATCH_DATA = json.load(f)
        print(f"📦 Loaded {len(KY_PATCH_DATA)} KY stocks from patch file: {KY_PATCH_FILE}")
    except Exception as e:
        print(f"⚠️ Error loading KY patch file: {e}")

# Hardcoded Pre-2003 Patches (Keep these as they are not in Goodinfo scan range usually)
PRE_2003_PATCHES = {
    "1808": {
        2000: {'cash': 0.0, 'stock': 2.0},
        2001: {'cash': 0.5, 'stock': 1.0},
        2002: {'cash': 0.0, 'stock': 0.0}, 
    }
}

async def reimport_dividends(start_year: int = 2003, end_year: int = 2025):
    """Re-crawl TWSE TWT49U and overwrite DuckDB dividends table."""
    crawler = TWSECrawler(data_dir="data/raw_dividends")
    conn = get_connection()
    
    # Efficiently fetch prices for yield checking (bulk)
    print("📈 Pre-fetching prices for yield sanity checks...")
    try:
        all_prices = conn.execute("SELECT stock_id, year(date) as year, AVG(close) as avg_price FROM daily_prices GROUP BY stock_id, year").df()
        price_map = all_prices.set_index(['stock_id', 'year'])['avg_price'].to_dict()
    except Exception:
        print("  ⚠️  Could not fetch prices (maybe DB empty?)")
        price_map = {}

    # 1. Backup Stats
    try:
        existing_count = conn.execute("SELECT COUNT(*) FROM dividends").fetchone()[0]
        print(f"📊 Existing DuckDB dividend records: {existing_count}")
    except:
        existing_count = 0
        
    # 2. Clear Table
    print("🗑️  Clearing existing dividend data...")
    conn.execute("DELETE FROM dividends")
    
    total_inserted = 0
    skipped_outliers = 0
    total_inserted = 0
    skipped_outliers = 0
    patched_count = 0
    ky_patched_count = 0
    
    # 3. Crawl Loop
    for year in range(start_year, end_year + 1):
        print(f"\n📅 Processing TWSE dividends for {year}...")
        try:
            # This uses the cache if available, or fetches if not
            div_data = await crawler.fetch_ex_rights_history(year)
            
            if not div_data:
                print(f"  ⚠️  No dividend data for {year}")
                continue
                
            # Step B: Insert with Patch Overlay
            rows_to_insert = []
            
            for stock_id, vals in div_data.items():
                cash = float(vals.get('cash', 0.0))
                stock = float(vals.get('stock', 0.0))
                is_combined = vals.get('_type') == 'combined'
                
                # Apply Goodinfo Patch
                patched = False
                if stock_id in PATCH_DATA and str(year) in PATCH_DATA[stock_id]:
                    p = PATCH_DATA[stock_id][str(year)]
                    cash = float(p.get('cash', 0.0))
                    stock = float(p.get('stock', 0.0))
                    patched = True
                    patched_count += 1
                elif is_combined:
                    # Unpatched Combined Row
                    # We have Total Value in 'cash' (from crawler), check if it's crazy
                    pass 

                # Apply KY/DR Patch (Higher Priority - Overwrites data for KY stocks)
                if stock_id in KY_PATCH_DATA:
                    ky_info = KY_PATCH_DATA[stock_id]
                    if 'dividends' in ky_info and str(year) in ky_info['dividends']:
                        p = ky_info['dividends'][str(year)]
                        cash = float(p.get('cash', 0.0))
                        stock = float(p.get('stock', 0.0))
                        # Explicitly mark as patched to avoid outlier skip
                        patched = True 
                        ky_patched_count += 1
                        # print(f"    Values patched from YFinance for {stock_id} ({year})")

                # Apply Pre-2003 Patch (if applicable)
                if year < 2003 and stock_id in PRE_2003_PATCHES and year in PRE_2003_PATCHES[stock_id]:
                     p = PRE_2003_PATCHES[stock_id][year]
                     cash = p.get('cash', cash)
                     stock = p.get('stock', stock)

                # SYSTEMIC SANITY CHECK
                avg_p = price_map.get((stock_id, year))
                if avg_p and cash > 0 and not patched:
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
                # print(f"  ✅ Inserted {len(rows_to_insert)} records for {year}")
            else:
                print(f"  ⚠️  No valid dividend records for {year}")
                
        except Exception as e:
            print(f"  ❌ Error for {year}: {e}")
            import traceback
            traceback.print_exc()

    # 4. Insert Pre-2003 Patches (If any explicitly defined outside crawl range)
    # The crawl loop covers start_year..end_year. If PRE_2003_PATCHES has years outside this range, insert them.
    # ... ignoring for now as we usually run from 2003.

    # 5. Final Verification
    new_count = conn.execute("SELECT COUNT(*) FROM dividends").fetchone()[0]
    print(f"\n{'='*60}")
    print(f"📊 Migration Complete!")
    print(f"   Before: {existing_count}")
    print(f"   After:  {new_count}")
    print(f"   Total Inserted: {total_inserted}")
    print(f"   Total Inserted: {total_inserted}")
    print(f"   Total Goodinfo Patched: {patched_count}")
    print(f"   Total KY/YFinance Patched: {ky_patched_count}")
    
    # Spot Check 2892
    print(f"\n🔍 Spot Check - 2892 (First Fin):")
    rows = conn.execute("SELECT year, cash, stock FROM dividends WHERE stock_id='2892' AND year >= 2020 ORDER BY year").fetchall()
    for r in rows:
        print(f"   {r[0]}: cash={r[1]:.2f}, stock={r[2]:.2f}")
        
    conn.close()

if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 2003
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 2025
    asyncio.run(reimport_dividends(start, end))
