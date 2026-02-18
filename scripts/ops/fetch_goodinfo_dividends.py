
import asyncio
import argparse
import json
import os
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

DATA_DIR = "data/raw_dividends"
REF_FILE = "data/ref/goodinfo_dividends.json"

def get_combined_stocks(start_year=2010, end_year=2025):
    """Scan TWT49U cache files for stocks with _type='combined'."""
    targets = set()
    print(f"🔍 Scanning TWT49U cache ({start_year}-{end_year}) for 'combined' entries...")
    
    for year in range(start_year, end_year + 1):
        cache_file = os.path.join(DATA_DIR, f"TWSE_Dividends_{year}.json")
        if not os.path.exists(cache_file):
            print(f"  ⚠️  Cache missing: {cache_file}")
            continue
            
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                
            for stock_id, info in data.items():
                if info.get('_type') == 'combined':
                    targets.add(stock_id)
        except Exception as e:
            print(f"  ❌ Error reading {cache_file}: {e}")
            
    print(f"✅ Found {len(targets)} unique stocks with combined dividends.")
    return sorted(list(targets))

def parse_dividend_policy(page, stock_id):
    """Parse Goodinfo Dividend Policy table."""
    url = f"https://goodinfo.tw/tw/StockDividendPolicy.asp?STOCK_ID={stock_id}"
    print(f"  globe Fetching {stock_id}...")
    
    try:
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        # Random sleep to be polite
        time.sleep(2)
        
        # Check if table exists. The main table usually has id usually works, 
        # but Goodinfo structure is complex. Look for text "股利發放年度".
        
        # We need to extract: Year, Cash Total, Stock Total
        # Table columns (approx):
        # 0: 股利發放年度
        # 1: 股利所屬年度
        # ...
        # Cash Dividend Total is usually col index ~3 (盈餘+公積)
        # Stock Dividend Total is usually col index ~6 (盈餘+公積)
        # Total Dividend is col ~7
        
        # Let's verify headers dynamically if possible, or use robust selectors
        
        # Goodinfo structure:
        # <div id="divDetail"> ... <table> ...
        # Header row: 股利發放期間 | 股利所屬期間 | ... | 現金股利(盈餘,公積,合計) | ...
        
        rows = page.query_selector_all("#divDetail table tr")
        
        results = {}
        
        header_map = {}
        data_start_idx = -1
        
        for i, row in enumerate(rows):
            text = row.inner_text().strip()
            # print(f"Row {i}: {text[:50]}")
            
            # Simple parsing strategy: Look for rows starting with a Year (e.g. "2024")
            # And extract values based on typical position.
            # Typical text row: "2024 2023 0.85 0 0.85 0.3 0 0.3 1.15 ..."
            
            # Columns: 
            # 0: Pay Year
            # 1: Ref Year
            # 2: Cash(Earnings)
            # 3: Cash(Reserve)
            # 4: Cash(Total)  <-- Target
            # 5: Stock(Earnings)
            # 6: Stock(Reserve)
            # 7: Stock(Total) <-- Target
            
            cols = text.split()
            if not cols: continue
            
            # Check if first col is a year (4 digits)
            if cols[0].isdigit() and len(cols[0]) == 4:
                year = int(cols[0])
                if year < 1990: continue 
                
                try:
                    # Valid data row usually has many numbers
                    if len(cols) < 8: continue
                    
                    cash_total = float(cols[4])
                    stock_total = float(cols[7])
                    
                    results[year] = {
                        'cash': cash_total,
                        'stock': stock_total
                    }
                except ValueError:
                    continue
                    
        return results

    except Exception as e:
        print(f"  ❌ Error processing {stock_id}: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(description="Fetch Goodinfo Dividends via Playwright")
    parser.add_argument("--incremental", action="store_true", help="Only fetch stocks not in ref file")
    parser.add_argument("--scan-cache", action="store_true", default=True, help="Scan TWT49U cache for targets")
    parser.add_argument("--targets", type=str, help="Comma-separated list of stock IDs to fetch")
    args = parser.parse_args()

    # 1. Load existing reference
    if os.path.exists(REF_FILE):
        with open(REF_FILE, 'r') as f:
            ref_data = json.load(f)
    else:
        ref_data = {}
    
    print(f"📂 Loaded {len(ref_data)} stocks from reference file.")

    # 2. Identify targets
    todo_stocks = []
    
    if args.targets:
        todo_stocks = args.targets.split(',')
    elif args.scan_cache:
        combined = get_combined_stocks()
        if args.incremental:
            # Filter out stocks already fully present? 
            # Ideally we check if *new* years are missing, but simpler: check if stock exists
            # Or assume if stock exists, we have history. 
            # For quarterly, we might need to re-fetch known stocks to get *this year's* data.
            # So --incremental might mean "Only fetch IF we suspect missing data".
            # For now, let's treat --incremental as "Add new stocks".
            # Post-crawl: if TWT49U has a Combined entry for 2024, and ref_data[stock][2024] is missing -> fetch.
            
            # Robust Incremental Logic:
            # Get all (stock, year) combos from cache that are Combined
            # Check if ref_data covers them.
            # If not, add stock to todo.
            
            needed_stocks = set()
            for year in range(2010, 2026):
                cache_file = os.path.join(DATA_DIR, f"TWSE_Dividends_{year}.json")
                if os.path.exists(cache_file):
                    with open(cache_file, 'r') as f:
                        cdata = json.load(f)
                        for sid, val in cdata.items():
                            if val.get('_type') == 'combined':
                                # Check if ref has this year
                                if str(year) not in ref_data.get(sid, {}):
                                    needed_stocks.add(sid)
            
            combined = sorted(list(needed_stocks))
            print(f"🔄 Incremental: Found {len(combined)} stocks needing updates.")
            
        todo_stocks = combined
    
    if not todo_stocks:
        print("✅ No stocks to fetch.")
        return

    print(f"🚀 Starting Playwright fetch for {len(todo_stocks)} stocks...")
    
    # 3. Launch Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()
        
        dirty = False
        avg_time = 0
        
        for i, stock_id in enumerate(todo_stocks):
            start_t = time.time()
            print(f"[{i+1}/{len(todo_stocks)}] Processing {stock_id}...")
            
            divs = parse_dividend_policy(page, stock_id)
            
            if divs:
                if stock_id not in ref_data:
                    ref_data[stock_id] = {}
                
                # Merge data (int keys to str for JSON)
                for y, d in divs.items():
                    ref_data[stock_id][str(y)] = d
                
                print(f"  ✅ Fetched {len(divs)} years.")
                dirty = True
            else:
                print(f"  ⚠️  No data found for {stock_id}")
                
            elapsed = time.time() - start_t
            avg_time = (avg_time * i + elapsed) / (i + 1)
            remaining = avg_time * (len(todo_stocks) - i - 1)
            # print(f"  ⏱️  Take {elapsed:.1f}s (Est. remaining: {remaining/60:.1f}m)")
            
            # Save intermediate
            if i % 10 == 0 and dirty:
                with open(REF_FILE, 'w') as f:
                    json.dump(ref_data, f, indent=2, sort_keys=True)
                dirty = False
        
        browser.close()
        
    # Final Save
    with open(REF_FILE, 'w') as f:
        json.dump(ref_data, f, indent=2, sort_keys=True)
    print(f"💾 Saved reference data to {REF_FILE}")

if __name__ == "__main__":
    main()
