import httpx
import asyncio
import os
import json
import datetime
# import pandas as pd # Lazy Import (already imported locally in fetch_market_prices_batch)
import time

class TPEXCrawler:
    def __init__(self, data_dir="data/raw"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _to_roc_date(self, date_obj):
        """Convert datetime/date object to ROC string (e.g. 113/01/01)"""
        roc_year = date_obj.year - 1911
        return f"{roc_year}/{date_obj.month:02d}/{date_obj.day:02d}"

    async def fetch_market_prices_batch(self, years: list, progress_callback=None):
        """
        Refactored: Fetch TPEx Market-Wide Prices using YFinance (Historical) 
        and st43 (Universe discovery).
        OPTIMIZED: Fetches full history (min_year to max_year) in one go to minimize requests.
        """
        import yfinance as yf
        import pandas as pd
        import asyncio
        
        # Initialize results structure
        results = {y: {} for y in years}
        
        # 0. Check Cache First
        years_to_fetch = []
        for year in years:
            cache_file = os.path.join(self.data_dir, f"TPEx_Market_{year}_Prices.json")
            use_cache = False
            if os.path.exists(cache_file):
                now = datetime.datetime.now()
                is_current_year = (year == now.year)
                
                if is_current_year:
                    mtime = os.path.getmtime(cache_file)
                    if (time.time() - mtime) < 86400: # Valid (<24h)
                        use_cache = True
                else:
                    use_cache = True # Historic always valid
            
            if use_cache:
                try:
                    with open(cache_file, 'r') as f:
                        results[year] = json.load(f)
                    print(f"Loaded TPEx Market Prices {year} from Cache.")
                except:
                    years_to_fetch.append(year)
            else:
                years_to_fetch.append(year)
        
        if not years_to_fetch:
            if progress_callback: progress_callback(1, 1)
            return results

        async with httpx.AsyncClient(verify=False) as client:
            # 1. Discover Universe (Today/Latest)

            print("Discovering TPEx Universe...")
            universe = await self._get_tpex_universe(client)
            print(f"TPEx Universe Size: {len(universe)}")
            
            if not universe:
                return {}

            # 2. Determine Date Range for Fetching
            if not years_to_fetch: return results
            
            min_year = min(years_to_fetch)
            max_year = max(years_to_fetch)
            start_date = f"{min_year}-01-01"
            
            # End Date should be Today or End of Max Year
            today = datetime.date.today()
            if max_year >= today.year:
                end_date = today.strftime("%Y-%m-%d")
            else:
                end_date = f"{max_year}-12-31"

            print(f"Fetching History {start_date} to {end_date} (Batch Optimized)...")

            # 3. Batch Fetch Full History
            batch_size = 100 # Increased from 30 for speed
            yf_tickers = [c + ".TWO" for c in universe]
            
            total = len(yf_tickers)
            for i in range(0, total, batch_size):
                batch = yf_tickers[i:i+batch_size]
                
                # Report Progress
                if progress_callback:
                    try:
                         # Use i + batch_size or total, bounded
                         current = min(i + batch_size, total)
                         progress_callback(current, total)
                    except: pass
                
                try:
                    # Rate Limit
                    if i > 0: await asyncio.sleep(1.0) # Reduced sleep
                    
                    df = await asyncio.to_thread(yf.download, batch, start=start_date, end=end_date, auto_adjust=False, progress=False)
                    
                    if df.empty: continue
                    if 'Close' not in df.columns: continue
                    
                    closes = df['Close']
                    # Iterate Tickers in this batch
                    for ticker in closes.columns:
                        series = closes[ticker].dropna()
                        if series.empty: continue
                        
                        code = ticker.replace('.TWO', '')
                        
                        # Process for EACH requested year
                        for year in years_to_fetch:
                            # Define Windows
                            y_start = f"{year}-01-01"
                            y_s_end = f"{year}-01-15"
                            
                            if year == today.year:
                                y_end = today.strftime("%Y-%m-%d")
                                y_e_start = (today - datetime.timedelta(days=10)).strftime("%Y-%m-%d")
                            else:
                                y_e_start = f"{year}-12-15"
                                y_e_end = f"{year}-12-31"
                            
                            # Extract Prices
                            # Start Price (First in Jan)
                            try:
                                s_slice = series.loc[y_start:y_s_end]
                                if not s_slice.empty:
                                    s_price = float(s_slice.iloc[0])
                                else:
                                    s_price = 0.0
                            except: s_price = 0.0
                            
                            # End Price (Last in Dec/Today)
                            try:
                                e_slice = series.loc[y_e_start:y_e_end]
                                if not e_slice.empty:
                                    e_price = float(e_slice.iloc[-1])
                                else:
                                    # Fallback: Try getting last price of the year
                                    # This handles cases where data exists but not in the rigid window
                                    y_full = series.loc[str(year)]
                                    if not y_full.empty:
                                         e_price = float(y_full.iloc[-1])
                                    else:
                                         e_price = 0.0
                            except: e_price = 0.0

                            # Update Result if we found data
                            if s_price > 0 or e_price > 0:
                                # Data Healing: If Start 0 but End > 0, assume Start=End (New Listing)
                                if s_price == 0 and e_price > 0: s_price = e_price
                                # Data Healing: If End 0 but Start > 0 (Suspended?), use Start
                                if e_price == 0 and s_price > 0: e_price = s_price
                                
                                results[year][code] = {
                                    'start': s_price,
                                    'end': e_price
                                }
                                
                except Exception as e:
                    print(f"  Batch Error: {e}")

        # 4. Save Cache Files
        for year, data in results.items():
            if data:
                cache_file = os.path.join(self.data_dir, f"TPEx_Market_{year}_Prices.json")
                with open(cache_file, 'w') as f:
                    json.dump(data, f)
                print(f"  Saved {year} cache ({len(data)} items)")
        
        return results

    async def _get_tpex_universe(self, client):
        # Use stk_quote_result.php (Latest) to get all codes
        url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
        params = {"l": "zh-tw", "o": "json"} # No 'd' -> Latest
        headers = {
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
             "X-Requested-With": "XMLHttpRequest"
        }
        
        codes = []
        try:
            resp = await client.get(url, params=params, headers=headers, timeout=15.0)
            if resp.status_code == 200:
                data = resp.json()
                # Parse aaData or Tables
                aaData = data.get('aaData', [])
                tables = data.get('tables', [])
                
                raw_rows = []
                if aaData: raw_rows = aaData
                elif tables:
                     for t in tables:
                         raw_rows.extend(t.get('data', []))
                
                for row in raw_rows:
                    if len(row) > 0:
                        code = row[0]
                        if code and code.strip():
                            # Filter: Keep only Stocks (4 digits) or ETFs (6 digits starting with 00)
                            c = code.strip()
                            is_bond_etf = len(c) == 6 and c.startswith('00') and c.endswith('B')
                            if (len(c) == 4 and c.isdigit()) or (len(c) == 6 and c.startswith('00') and c.isdigit()) or is_bond_etf:
                                codes.append(c)
        except Exception as e:
            print(f"Error getting universe: {e}")
            
        return list(set(codes))

    async def fetch_ex_rights_history(self, year: int):
        """
        Fetch Dividend History for TPEx stocks using YFinance.
        Returns dict: {stock_code: {'cash': float, 'stock': float}}
        """
        import yfinance as yf
        import logging
        import asyncio
        import json
        
        # Silence yfinance "possibly delisted" spam
        logging.getLogger('yfinance').setLevel(logging.CRITICAL)
        logging.getLogger('yahoo_utils').setLevel(logging.CRITICAL)
        
        results = {}
        
        # 0. Check Cache
        cache_file = os.path.join(self.data_dir, f"TPEx_Dividends_{year}.json")
        if os.path.exists(cache_file):
            use_cache = False
            now = datetime.datetime.now()
            if year == now.year:
                 mtime = os.path.getmtime(cache_file)
                 if (time.time() - mtime) < 86400: 
                     use_cache = True
            else:
                 use_cache = True
                 
            if use_cache:
                try:
                    with open(cache_file, 'r') as f:
                        results = json.load(f)
                    print(f"Loaded TPEx Dividends for Year {year} from Cache ({len(results)} items).")
                    return results
                except Exception as e:
                    print(f"Error loading cache for {year}: {e}")

        # 1. Get Universe

        async with httpx.AsyncClient(verify=False) as client:
            universe = await self._get_tpex_universe(client)
            
        print(f"Fetching Dividends for {len(universe)} TPEx stocks (Year {year})...")
        
        import socket
        socket.setdefaulttimeout(15) # Prevent infinite hangs
        
        # 2. Batch Processing (Optimized: larger batches, shorter sleep)
        batch_size = 50 # Increased from 10 for speed
        yf_tickers = [c + ".TWO" for c in universe]
        
        total = len(yf_tickers)
        for i in range(0, total, batch_size):
            if i % 100 == 0:
                print(f"  Processing TPEx Dividend Batch {i}/{total}...")
            batch = yf_tickers[i:i+batch_size]
            
            try:
                if i > 0: await asyncio.sleep(0.3)  # Reduced from duplicate 0.5+0.5
                
                # Define scope vars for interior function
                s_date = f"{year}-01-01"
                e_date = f"{year}-12-31" 
                
                # Run blocking yfinance IO in a separate thread
                def fetch_batch_history():
                    batch_results = {}
                    tickers_obj = yf.Tickers(" ".join(batch))
                    
                    for ticker_id, ticker_obj in tickers_obj.tickers.items():
                         try:
                             # Sync call
                             hist = ticker_obj.history(start=s_date, end=e_date, actions=True)
                             if hist.empty: continue
                             
                             code = ticker_id.replace('.TWO', '')
                             
                             cash_div = 0.0
                             stock_div_par = 0.0
                             
                             if 'Dividends' in hist.columns:
                                 cash_div = hist['Dividends'].sum()
                                 
                             if 'Stock Splits' in hist.columns:
                                 splits = hist[hist['Stock Splits'] != 0]['Stock Splits']
                                 for date, ratio in splits.items():
                                     if ratio > 1.0:
                                         sdf = (ratio - 1.0) * 10.0
                                         stock_div_par += sdf
                                         
                             if cash_div > 0 or stock_div_par > 0:
                                 batch_results[code] = {
                                     'cash': float(cash_div),
                                     'stock': float(stock_div_par)
                                 }
                         except Exception:
                             pass
                    return batch_results

                # Await the thread
                batch_data = await asyncio.to_thread(fetch_batch_history)
                results.update(batch_data)
                        
            except Exception as e:
                print(f"  Batch Error: {e}")
                
        # Cache logic if needed, but for now just return results
        # Calling logic handles merging
        
        if True: # Always cache to prevent re-scanning empty years
            cache_file = os.path.join(self.data_dir, f"TPEx_Dividends_{year}.json")
            with open(cache_file, 'w') as f:
                json.dump(results, f)
            print(f"Saved TPEx Dividends to {cache_file} ({len(results)} items)")
        
        return results
