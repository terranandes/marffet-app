import httpx
import asyncio
import os
import json
import datetime
import pandas as pd
import time

class TPEXCrawler:
    def __init__(self, data_dir="data/raw"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _to_roc_date(self, date_obj):
        """Convert datetime/date object to ROC string (e.g. 113/01/01)"""
        roc_year = date_obj.year - 1911
        return f"{roc_year}/{date_obj.month:02d}/{date_obj.day:02d}"

    async def fetch_market_prices_batch(self, years: list):
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
        
        async with httpx.AsyncClient(verify=False) as client:
            # 1. Discover Universe (Today/Latest)
            print("Discovering TPEx Universe...")
            universe = await self._get_tpex_universe(client)
            print(f"TPEx Universe Size: {len(universe)}")
            
            if not universe:
                return {}

            # 2. Determine Date Range
            min_year = min(years)
            max_year = max(years)
            start_date = f"{min_year}-01-01"
            
            # End Date should be Today or End of Max Year
            today = datetime.date.today()
            if max_year >= today.year:
                end_date = today.strftime("%Y-%m-%d")
            else:
                end_date = f"{max_year}-12-31"

            print(f"Fetching History {start_date} to {end_date} (Batch Optimized)...")

            # 3. Batch Fetch Full History
            batch_size = 30
            yf_tickers = [c + ".TWO" for c in universe]
            
            total = len(yf_tickers)
            for i in range(0, total, batch_size):
                batch = yf_tickers[i:i+batch_size]
                
                try:
                    # Rate Limit
                    if i > 0: await asyncio.sleep(2.0)
                    
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
                        for year in years:
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
                            if (len(c) == 4 and c.isdigit()) or (len(c) == 6 and c.startswith('00') and c.isdigit()):
                                codes.append(c)
        except Exception as e:
            print(f"Error getting universe: {e}")
            
        return list(set(codes))

    async def fetch_ex_rights_history(self, start_year, end_year):
        """
        Fetch Dividend History.
        To be implemented.
        """
        print("TPEx Dividend Fetching not yet implemented.")
        return {}

    async def fetch_ex_rights_history(self, start_year, end_year):
        """
        Fetch Dividend History.
        To be implemented (HTML Parsing).
        For now returns empty dict to avoid breaking pipeline.
        """
        print("TPEx Dividend Fetching not yet implemented.")
        return {}
