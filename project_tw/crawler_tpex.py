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
        Fetch TPEx Market-Wide Prices (Start/End) using Daily Quotes (stk_quote_result.php).
        Returns: {year: {code: {'start': float, 'end': float}}}
        """
        results = {}
        async with httpx.AsyncClient() as client:
            for year in years:
                # Cache File (TPEx specific prefix)
                cache_file = os.path.join(self.data_dir, f"TPEx_Market_{year}_Prices.json")
                if os.path.exists(cache_file):
                    # Check if it's the current year and might be stale?
                    # For simplicty, reuse same logic as TWSE (manual clean needed for fresh)
                    # BUT we can check modification time if needed. 
                    # Let's trust the "clean_current_run.sh" user habit.
                    print(f"CACHE HIT: {cache_file}")
                    with open(cache_file, 'r') as f:
                        results[year] = json.load(f)
                    continue
                    
                print(f"CACHE MISS: Fetching {year} TPEx Market Prices...")
                y_data = {}
                
                # Fetch Start (Jan)
                # Try Jan 2..10. TPEx might have different trading days, but likely same.
                start_dates = [datetime.date(year, 1, d) for d in range(2, 8)]
                s_prices = await self._fetch_market_day(client, start_dates, "Start")
                
                # Fetch End (Dec or Today)
                today = datetime.date.today()
                if year == today.year:
                    # Current year: scan backward from today
                    print(f"DEBUG: Current Year {year} (TPEx). Scanning backward from {today}...")
                    end_dates = [today - datetime.timedelta(days=i) for i in range(7)]
                else:
                    # Historic: Dec 31..24
                    end_dates = [datetime.date(year, 12, d) for d in range(31, 24, -1)]
                
                e_prices = await self._fetch_market_day(client, end_dates, "End")
                
                # Combine
                all_codes = set(s_prices.keys()) | set(e_prices.keys())
                for c in all_codes:
                    y_data[c] = {
                        'start': s_prices.get(c, 0.0),
                        'end': e_prices.get(c, 0.0)
                    }
                
                results[year] = y_data
                
                # Save Cache (Only if data exists)
                if y_data:
                    with open(cache_file, 'w') as f:
                        json.dump(y_data, f)
                else:
                    print(f"Warning: No data fetched for {year}. Skipping cache save.")
                    
        return results

    async def _fetch_market_day(self, client, candidates, label):
        """
        Try candidate dates until valid data is found.
        candidates: list of datetime.date objects
        """
        url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw"
        }
        
        for date_obj in candidates:
            roc_date = self._to_roc_date(date_obj)
            params = {
                "l": "zh-tw",
                "d": roc_date,
                "o": "json"
            }
            
            try:
                await asyncio.sleep(1.0) # Rate limit
                print(f"Fetching TPEx {label}: {roc_date}...")
                resp = await client.get(url, params=params, headers=headers, timeout=15.0)
                
                if resp.status_code != 200:
                    print(f"  HTTP Error {resp.status_code}")
                    continue
                
                try: 
                    data = resp.json()
                except ValueError:
                    print(f"  JSON Decode Error. Content preview: {resp.text[:200]}")
                    continue

                # Check for aaData (Old Schema) or tables (New Schema)
                aaData = data.get('aaData', [])
                tables = data.get('tables', [])
                
                prices = {}
                
                if aaData:
                    # Logic for aaData
                    for row in aaData:
                        try:
                            # Index 0: Code, Index 2: Close usually?
                            code = row[0]
                            price_str = row[2] 
                            if price_str == '---' or price_str == '':
                                continue
                            price_val = float(price_str.replace(',', ''))
                            prices[code] = price_val
                        except:
                            continue
                            
                elif tables:
                    # Logic for Tables (TWSE style)
                    print(f"  Found {len(tables)} tables. Scanning...")
                    for i, t in enumerate(tables):
                        title = t.get('title', '')
                        rows = t.get('data', [])
                        # Search for Price Table
                        # Usually contains "收盤" (Closing)
                        # Or just scan ALL tables for Code + Price?
                        # Let's inspect rows.
                        if not rows:
                            continue
                            
                        # Sample row check - REMOVED DEBUG PRINTS
                        
                        # Inspect rows
                        for row in rows:
                             try:
                                 code = row[0]
                                 # Heuristic: If row has > 2 cols, try col 2 as price?
                                 if len(row) > 2:
                                     p_str = row[2]
                                     if isinstance(p_str, str):
                                         p_str = p_str.replace(',', '')
                                         # Check if float
                                         if p_str.replace('.','').isdigit() or (p_str.replace('.','').replace('-','').isdigit() and '-' in p_str): # Handle negative/float
                                            # Wait, prices are positive. But change is +/-
                                            # Close price is positive.
                                             try:
                                                 prices[code] = float(p_str)
                                             except:
                                                 pass
                             except:
                                 pass
                                 
                else:
                    print(f"  No aaData or tables found. Keys: {list(data.keys())}")
                    continue

                if prices:
                    print(f"  Got {len(prices)} items from {roc_date}")
                    return prices
                    
            except Exception as e:
                print(f"  Error fetching {roc_date}: {e}")
                
        # If loop finishes without return
        print(f"Warning: No TPEx data found for {label} in candidates.")
        return {}

    async def fetch_ex_rights_history(self, start_year, end_year):
        """
        Fetch Dividend History.
        To be implemented (HTML Parsing).
        For now returns empty dict to avoid breaking pipeline.
        """
        print("TPEx Dividend Fetching not yet implemented.")
        return {}
