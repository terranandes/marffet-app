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
        import datetime
        
        results = {}
        sem = asyncio.Semaphore(12)

        async def fetch_one_year(year):
            async with sem:
                cache_file = os.path.join(self.data_dir, f"TPEx_Market_{year}_Prices.json")
                if os.path.exists(cache_file):
                    now = datetime.datetime.now()
                    is_current_year = (year == now.year)
                    use_cache = True
                    if is_current_year:
                        mtime = os.path.getmtime(cache_file)
                        if (time.time() - mtime) > 86400:
                             use_cache = False
                    if use_cache:
                        print(f"CACHE HIT TPEx: {cache_file}")
                        with open(cache_file, 'r') as f:
                            return year, json.load(f)
                
                print(f"CACHE MISS: Fetching {year} TPEx Market Prices via YFinance...")
                import yfinance as yf
                import logging
                logging.getLogger('yfinance').setLevel(logging.CRITICAL)
                
                async with httpx.AsyncClient(verify=False) as client:
                    universe = await self._get_tpex_universe(client)
                
                yf_tickers = [c + ".TWO" for c in universe]
                batch_size = 50
                year_data = {}
                
                def _fetch_batch(batch):
                    batch_res = {}
                    tickers_obj = yf.Tickers(" ".join(batch))
                    for ticker_id, ticker_obj in tickers_obj.tickers.items():
                        try:
                            # Use auto_adjust=False to get NOMINAL prices for bounds
                            hist = ticker_obj.history(start=f"{year}-01-01", end=f"{year+1}-01-01", auto_adjust=False)
                            if not hist.empty:
                                code = ticker_id.replace('.TWO', '')
                                start_p = float(hist['Close'].iloc[0])
                                end_p = float(hist['Close'].iloc[-1])
                                if start_p > 0 or end_p > 0:
                                    batch_res[code] = {'start': start_p, 'end': end_p}
                        except Exception:
                            pass
                    return batch_res

                # Batch processing
                total = len(yf_tickers)
                for i in range(0, total, batch_size):
                    batch = yf_tickers[i:i+batch_size]
                    if i > 0:
                        await asyncio.sleep(0.3)
                    batch_data = await asyncio.to_thread(_fetch_batch, batch)
                    year_data.update(batch_data)
                    
                if year_data:
                    with open(cache_file, 'w') as f:
                        json.dump(year_data, f)
                return year, year_data

        completed = 0
        total = len(years)
        async def fetch_wrapper(y):
            res = await fetch_one_year(y)
            nonlocal completed
            completed += 1
            if progress_callback:
                try:
                    progress_callback(completed, total)
                except Exception:
                    pass
            return res

        tasks = [fetch_wrapper(y) for y in years]
        results_list = await asyncio.gather(*tasks)
        for y, r in results_list:
            if r:
                results[y] = r

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
                if aaData:
                    raw_rows = aaData
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
                if i > 0:
                    await asyncio.sleep(0.3)  # Reduced from duplicate 0.5+0.5
                
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
                             if hist.empty:
                                 continue 
                             
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
