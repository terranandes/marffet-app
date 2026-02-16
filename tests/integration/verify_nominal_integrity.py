"""
Phase 14 Verification: Nominal Data Integrity

Verifies that the Market DB contains correct NOMINAL (unadjusted) prices.
Run this during or after the rebuild process to validate data quality.

Checks:
1. **Market Tag Consistency**: Ensure 'TWSE' is used (no 'TWSE_NOMINAL' or mixed tags).
2. **Nominal Price Validation**: Check known historical highs/lows for key stocks.
   - 2330 (TSMC): Should be > 600 in 2021/2022 (adjusted price would be much lower if splits were applied wrong, though TSMC splits are old).
   - 0050: Check price levels.
   - Key checks: Adjusted prices back-propagate splits/divs, so ancient prices become tiny.
     Nominal prices should remain at their historical traded levels (e.g., TSMC was ~200 in 2000, not $5).
3. **Data Continuity**: Check for massive gaps in sliding window (excluding weekends).
"""

import duckdb
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.getcwd())
from app.services.market_db import DB_PATH

def get_conn():
    if not DB_PATH.exists():
        print(f"❌ DB not found at {DB_PATH}")
        sys.exit(1)
    return duckdb.connect(str(DB_PATH), read_only=True)

def verify_market_tags(conn):
    print("\n🔍 Checking Market Tags...")
    df = conn.execute("SELECT market, COUNT(*) as count FROM daily_prices GROUP BY market").df()
    print(df)
    
    valid_tags = {'TWSE', 'TPEx'} # TPEx might exist from old data, TWSE is the new standard
    found_tags = set(df['market'].unique())
    
    if 'TWSE_NOMINAL' in found_tags:
        print("❌ FAIL: Found legacy 'TWSE_NOMINAL' tag. Migration incomplete.")
        return False
        
    print("✅ Market tags look consistent.")
    return True

def verify_nominal_prices(conn):
    print("\n🔍 Checking Nominal Price Levels (2330 TSMC)...")
    
    # TSMC (2330) History Check
    # In 2000, TSMC traded ~200 TWD.
    # Adjusted price (for 20+ years of dividends) would be < 50 TWD.
    # We want NOMINAL prices, so we expect ~200.
    
    query = """
        SELECT date, close 
        FROM daily_prices 
        WHERE stock_id = '2330' AND date BETWEEN '2000-01-01' AND '2000-12-31'
        ORDER BY date ASC
    """
    df_2000 = conn.execute(query).df()
    
    if df_2000.empty:
        print("⚠️ No TSMC data for 2000 yet (rebuild started from 2004?). Skipping 2000 check.")
    else:
        avg_close = df_2000['close'].mean()
        print(f"   Avg Close in 2000: {avg_close:.2f}")
        if avg_close < 100:
            print("❌ FAIL: TSMC 2000 prices look ADJUSTED (too low). Expected > 100.")
            return False
        else:
            print("✅ TSMC 2000 prices verify as NOMINAL (> 100).")

    # Check 2004 Data (since rebuild starts from 2004)
    print("\n🔍 Checking Nominal Price Levels (2330 TSMC - 2004)...")
    query_2004 = """
        SELECT date, close 
        FROM daily_prices 
        WHERE stock_id = '2330' AND date BETWEEN '2004-01-01' AND '2004-12-31'
    """
    df_2004 = conn.execute(query_2004).df()
    
    if df_2004.empty:
        print("⚠️ No TSMC data for 2004 yet.")
    else:
        avg_close = df_2004['close'].mean()
        print(f"   Avg Close in 2004: {avg_close:.2f}")
        # In 2004, TSMC traded ~60 TWD. Adjusted price would be < 15.
        if avg_close < 30:
            print("❌ FAIL: TSMC 2004 prices look ADJUSTED (too low). Expected > 30.")
            return False
        else:
            print("✅ TSMC 2004 prices verify as NOMINAL (> 30).")

    # Check 2330 Highs in 2022
    # Historical high was ~688 in Jan 2022.
    query_2022 = """
        SELECT MAX(high) as max_high
        FROM daily_prices 
        WHERE stock_id = '2330' AND date BETWEEN '2022-01-01' AND '2022-12-31'
    """
    max_2022 = conn.execute(query_2022).fetchone()[0]
    
    if max_2022 is None:
         print("⚠️ No TSMC data for 2022 yet.")
    else:
        print(f"   Max High in 2022: {max_2022}")
        if max_2022 > 680:
            print("✅ TSMC 2022 High validates (~688).")
        else:
            print(f"⚠️ TSMC 2022 High {max_2022} seems low (expected ~688).")

    return True

def verify_continuity(conn):
    print("\n🔍 Checking Data Continuity (Sample: 0050)...")
    df = conn.execute("""
        SELECT date FROM daily_prices 
        WHERE stock_id = '0050' 
        ORDER BY date ASC
    """).df()
    
    if df.empty:
        print("⚠️ No 0050 data found.")
        return True
        
    df['date'] = pd.to_datetime(df['date'])
    df['diff'] = df['date'].diff().dt.days
    
    # Check for gaps > 10 days
    gaps = df[df['diff'] > 10]
    if not gaps.empty:
        print(f"⚠️ Found {len(gaps)} large gaps (>10 days) in 0050 data:")
        print(gaps.head())
        # Not a hard failure because holidays/market closures exist, but >10 days is suspicious
        if len(gaps) > 5:
             print("❌ FAIL: Too many large gaps.")
             return False
             
    print("✅ Continuity check pass (no systematic gaps).")
    return True

def main():
    conn = get_conn()
    try:
        ok_tags = verify_market_tags(conn)
        ok_price = verify_nominal_prices(conn)
        ok_cont = verify_continuity(conn)
        
        if ok_tags and ok_price and ok_cont:
            print("\n🎉 ALL CHECKS PASSED. Data appears to be NOMINAL and CONSISTENT.")
            sys.exit(0)
        else:
            print("\n💥 VALIDATION FAILED. Check logs above.")
            sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
