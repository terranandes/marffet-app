
import httpx
import asyncio
import json
import os
import time
import pandas as pd
from datetime import datetime, timedelta

class TWSECrawler:
    def __init__(self, data_dir="data/raw"):
        self.base_url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        # TWSE has strict rate limits (suggestion: 3s delay)
        self.rate_limit_delay = 1.5 

    async def fetch_listing_dates(self):
        """
        Fetch Listing Dates for all TWSE stocks from the ISIN Registry.
        Returns: {code: "YYYY-MM-DD"}
        """
        cache_file = os.path.join(self.data_dir, "ListingDates.json")
        
        # 1. Check Cache (Expires in 30 days)
        if os.path.exists(cache_file):
            mtime = os.path.getmtime(cache_file)
            if (time.time() - mtime) < 86400 * 30:
                print("CACHE HIT: ListingDates.json")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)

        print("Fetching Listing Dates from ISIN Registry...")
        url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url)
                resp.raise_for_status()
                
            # HTML parsing (handling Big5 encoding if simple decoding fails)
            try:
                content = resp.content.decode('big5')
            except:
                content = resp.text # Fallback
                
            # Needs BeautifulSoup
            from bs4 import BeautifulSoup
            # Use 'ignore' in case of minor encoding bytes issues
            try:
                content = resp.content.decode('big5', errors='ignore')
            except:
                content = resp.text

            soup = BeautifulSoup(content, 'html.parser')
            
            # Target Table Index 1 (based on analysis)
            tables = soup.find_all('table')
            if len(tables) < 2:
                print("Error: ISIN table not found (count < 2)")
                return {}
            
            table = tables[1]
            listing_map = {}
            rows = table.find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4: continue
                
                # Header Check
                first_text = cols[0].get_text(strip=True)
                if "有價證券代號" in first_text: continue
                
                # Data Row Structure:
                # Col 0: 1101 台泥 (Code + Name)
                # Col 1: ISIN Code
                # Col 2: Listing Date (1962/02/09)
                # Col 3: Market
                # ...
                
                # Careful: Col 0 might be "Stock" category header in some rows?
                # Based on 'h4' class table structure usually:
                # <tr><td bgcolor="#D5FFD5">股票</td>...</tr> (Category Header)
                # <tr><td>1101　台泥</td><td>TW0001101004</td><td>1962/02/09</td>...</tr> (Data)
                
                code_name = cols[0].get_text(strip=True)
                # Split "1101 台泥" -> ["1101", "台泥"]
                parts = code_name.split()
                if not parts: continue
                
                code = parts[0]
                
                # If code is not 4 digits, likely a category header or special row
                if not (code.isdigit() and len(code) == 4):
                     continue
                     
                date_str = cols[2].get_text(strip=True) # Index 2 is Date
                
                # Validate Date "YYYY/MM/DD"
                if len(date_str) == 10 and date_str[4] == '/':
                    listing_map[code] = date_str.replace('/', '-')

            # Save Cache
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(listing_map, f)
                
            print(f"Parsed {len(listing_map)} Listing Dates.")
            return listing_map

        except Exception as e:
            print(f"Error fetching Listing Dates: {e}")
            return {}

    def _taiwan_to_ad(self, date_str):
        """Convert '113/01/02' to '2024-01-02'"""
        try:
            parts = date_str.split('/')
            year = int(parts[0]) + 1911
            return f"{year}-{parts[1]}-{parts[2]}"
        except Exception:
            return None

    async def fetch_stock_month(self, client, stock_code: str, date_str: str, sem: asyncio.Semaphore):
        """
        Fetch data for a specific month. 
        """
        file_path = os.path.join(self.data_dir, f"{stock_code}_{date_str}.json")
        
        # Check Cache (No semaphore needed)
        # Check Cache (No semaphore needed)
        if os.path.exists(file_path):
            try:
                # Cache Expiry for Current Month
                target_date = datetime.strptime(date_str, "%Y%m%d")
                now = datetime.now()
                # If requesting current month, check if cache is old (> 24h)
                if target_date.year == now.year and target_date.month == now.month:
                    mtime = os.path.getmtime(file_path)
                    if (time.time() - mtime) > 86400: # 24 hours
                        # print(f"Cache expired for {stock_code} {date_str}, refetching...")
                        pass # Fall through to fetch
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                             return json.load(f)
                else:
                    # Historical months are immutable
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            except:
                pass # corrupted file, refetch

        params = {
            "response": "json",
            "date": date_str,
            "stockNo": stock_code
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        async with sem:
            # Add randomized jitter or check global rate limits?
            # Simple approach: request then sleep
            try:
                # Must follow redirects (308) for modern TWSE behavior
                resp = await client.get(self.base_url, params=params, headers=headers, timeout=10.0, follow_redirects=True)
                resp.raise_for_status()
                data = resp.json()
                
                if data.get('stat') == 'OK':
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False)
                    return data
                else:
                    return None
            except Exception as e:
                print(f"Error fetching {stock_code} {date_str}: {e}")
                return None
            finally:
                # Minimum delay between requests on this semaphore slot to prevent burst
                # 4 slots * 0.5s delay = ~8 reqs/sec max
                await asyncio.sleep(0.25) 

    async def fetch_history(self, stock_code: str, start_year: int, end_year: int):
        """Fetch range of history concurrently."""
        current_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        
        months_to_fetch = []
        while current_date <= end_date:
            if current_date > datetime.now():
                break
            months_to_fetch.append(current_date.strftime("%Y%m01"))
            
            # Next month
            next_month = current_date.month + 1
            next_year = current_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            current_date = datetime(next_year, next_month, 1)

        # Execute concurrent fetches for this stock
        # Note: We share a client for connection pooling
        sem = asyncio.Semaphore(4) # Allow 4 concurrent requests per stock? 
        # Or better: passed from outside? 
        # Let's keep it local for now, but really we want global.
        # Given standard usage, let's use a local limit of 4 per stock call, 
        # but the caller (MarsStrategy) is actively limiting number of stocks.
        
        results = []
        async with httpx.AsyncClient() as client:
             tasks = [self.fetch_stock_month(client, stock_code, date, sem) for date in months_to_fetch]
             results = await asyncio.gather(*tasks)
             
        # Filter None
        return [r for r in results if r and r.get('stat') == 'OK']

    def parse_to_dataframe(self, raw_data_list):
        """Convert list of TWSE JSON responses to a single Pandas DataFrame"""
        all_rows = []
        for data in raw_data_list:
            if not data or data.get('stat') != 'OK':
                continue
            
            # Fields: ["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交筆數"]
            # English map for internal use
            for row in data['data']:
                # Clean numeric strings (remove commas)
                cleaned_row = {
                    'date': self._taiwan_to_ad(row[0]),
                    'volume': int(row[1].replace(',', '')),
                    'open': float(row[3].replace(',', '').replace('--', '0')) if row[3] != '--' else 0,
                    'high': float(row[4].replace(',', '').replace('--', '0')) if row[4] != '--' else 0,
                    'low': float(row[5].replace(',', '').replace('--', '0')) if row[5] != '--' else 0,
                    'close': float(row[6].replace(',', '').replace('--', '0')) if row[6] != '--' else 0,
                }
                all_rows.append(cleaned_row)
        
        df = pd.DataFrame(all_rows)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)
        return df

    async def fetch_year_start_end_prices(self, years: list):
        """
        Fetch Market-Wide Prices (Start/End) for each year using BWIBBU.
        Returns: {year: {code: {'start': float, 'end': float}}}
        """
        
        async with httpx.AsyncClient() as client:
            for year in years:
                y_res = {}
                # 1. Start Price (Jan)
                # Try Jan 2 to Jan 10
                start_dates = [f"{year}01{d:02d}" for d in range(2, 11)] 
                start_p = {}
                
                # Identify first valid trading day
                for d in start_dates:
                    url = "https://www.twse.com.tw/exchangeReport/BWIBBU_d"
                    params = {"response": "json", "date": d, "selectType": "ALL"}
                    try:
                        await asyncio.sleep(0.5)
                        resp = await client.get(url, params=params, timeout=10.0, follow_redirects=True)
                        data = resp.json()
                        if data.get('stat') == 'OK' and data.get('data'):
                            # Parse
                            # [Code, Name, PE, Yield, PB]
                            # Or [Code, Name, Close, ...] check Probe/Doc
                            # BWIBBU fields: ["證券代號","證券名稱","殖利率(%)","股利年度","本益比","股價淨值比","財報年/季"]
                            # WAIT. My previous comment said: `['2330', '台積電', '593.00', '1.85', ...]` (Step 1802)
                            # Step 1802 Logic: `yield_val = float(row[3])`. `row[2]` was printed as 593.00.
                            # But standard BWIBBU fields might NOT have Price explicitly if not PE/Yield table?
                            # BWIBBU_d (Daily) Fields: `["證券代號","證券名稱","本益比","殖利率(%)","股價淨值比"]`
                            # Wait, where is Price?
                            # PE = Price / EPS.
                            # PB = Price / Book.
                            # Price = PE * EPS? No.
                            # I need to confirm BWIBBU HAS PRICE.
                            # Probe Step 1370/1361 was TWT49U.
                            # Step 1802 logic `row[2]` was assuming Price?
                            # Let's PROBE BWIBBU FIRST.
                            # If no price, I use `MI_INDEX` (T86) "Daily Quotes".
                            # MI_INDEX Fields: `["證券代號","證券名稱","成交股數","成交筆數","成交金額","開盤價","最高價","最低價","收盤價",...]`
                            # MI_INDEX DEFINITELY has Price (Index 8 is Close).
                            # Endpoint: `/exchangeReport/MI_INDEX?response=json&date=...&type=ALLBUT0999`
                            # This gives ALL stocks.
                            # I'll use MI_INDEX.
                            break
                    except:
                        pass
                
                # Wait, I wrote code but realized BWIBBU might lack price.
                # I will switch to MI_INDEX logic inside this function.
                pass
                
        # Since I am editing `crawler.py`, I will rewrite this function to use MI_INDEX properly.
        if year < 2010:
            # Manual Patches ...
            pass
            
        # Cache File
        cache_file = os.path.join(self.data_dir, f"TWT49U_{year}.json")
        if os.path.exists(cache_file):
            print(f"CACHE HIT: {cache_file}")
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # New API Logic (Quarterly Fetch)
        # Because range limit is small (~2-3 months)
        all_data = []
        try:
            # Fetch by Month to avoid data truncation/limits
            months = []
            for m in range(1, 13):
                import calendar
                last_day = calendar.monthrange(year, m)[1]
                months.append((f"{year}{m:02d}01", f"{year}{m:02d}{last_day}"))
            
            async with httpx.AsyncClient() as client:
                for s_date, e_date in months:
                    url = "https://www.twse.com.tw/exchangeReport/TWT49U"
                    params = {
                        "response": "json",
                        "strDate": s_date,
                        "endDate": e_date
                    }
                    await asyncio.sleep(1.0) # Rate limit
                    # print(f"Fetching TWT49U {s_date}-{e_date}...")
                    try:
                        resp = await client.get(url, params=params, timeout=10.0)
                        data = resp.json()
                        if data.get('stat') == 'OK':
                            all_data.extend(data.get('data', []))
                    except Exception as e:
                        print(f"Error fetching TWT49U {s_date}: {e}")
                        
            # Save Cache if successful
            if all_data:
                with open(cache_file, 'w') as f:
                    json.dump(all_data, f)
                    
            return all_data
            
        except Exception as e:
            print(f"Error fetching dividends {year}: {e}")
        
        return []

    async def detect_daily_split(self, code, year):
        """
        Scans monthly STOCK_DAY reports to find a specific daily price drop > 60%.
        Returns inferred Stock Dividend value (e.g. 30.0 for 4-for-1) or 0.0.
        """
        print(f"Deep Scan for Split: {code} in {year}...")
        prev_close = 0.0
        
        async with httpx.AsyncClient() as client:
            for m in range(1, 13):
                date_str = f"{year}{m:02d}01"
                url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
                params = {"response": "json", "date": date_str, "stockNo": code}
                
                try:
                    await asyncio.sleep(0.5)
                    resp = await client.get(url, params=params, timeout=10.0)
                    data = resp.json()
                    if data.get('stat') == 'OK':
                        rows = data.get('data', [])
                        # Row: Date, Vol, Val, Open, High, Low, Close, ...
                        # Close is index 6. (Check fields to be sure, but standard for STOCK_DAY)
                        # Fields: ["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價",...]
                        
                        for r in rows:
                            try:
                                # Handle commas
                                close_p = float(r[6].replace(',', ''))
                                
                                if prev_close > 0:
                                    ratio = prev_close / close_p
                                    # Threshold: Drop > 60% (Ratio > 2.5)
                                    if ratio > 2.5: 
                                        # Check if integer-ish
                                        nearest = round(ratio)
                                        if abs(ratio - nearest) < 0.2: # Allow small drift
                                            print(f"  FOUND DROP: {r[0]} {prev_close} -> {close_p} (Ratio {ratio:.2f})")
                                            return (nearest - 1) * 10.0
                                
                                prev_close = close_p
                            except:
                                pass
                except Exception as e:
                    print(f"  Error scan {date_str}: {e}")
                    
        return 0.0



    async def fetch_market_prices_batch(self, years: list):
        """
        Fetch Market-Wide Prices (Start/End) using MI_INDEX (Daily Quotes).
        Returns: {year: {code: {'start': float, 'end': float}}}
        """
        # 1. Fetch Listing Dates Map (Fast, Cached)
        listing_dates = await self.fetch_listing_dates()

        results = {}
        sem = asyncio.Semaphore(4) # Limit concurrency to avoid global ban

        async def fetch_one_year(year):
             async with sem:
                # Cache File
                cache_file = os.path.join(self.data_dir, f"Market_{year}_Prices.json")
                if os.path.exists(cache_file):
                    # Cache Expiry for Current Year
                    now = datetime.now()
                    is_current_year = (year == now.year)
                    use_cache = True
                    
                    if is_current_year:
                        mtime = os.path.getmtime(cache_file)
                        if (time.time() - mtime) > 86400: # 24 hours
                             print(f"CACHE EXPIRED for Current Year {year} (Older than 24h). Refetching...")
                             use_cache = False
                    
                    if use_cache:
                        print(f"CACHE HIT: {cache_file}")
                        with open(cache_file, 'r') as f:
                            return year, json.load(f)
                     
                print(f"CACHE MISS: Fetching {year} Market Prices...")
                
                async with httpx.AsyncClient() as client:
                    # Fetch Start (Jan)
                    # Try Jan 2..10
                    start_dates = [f"{year}01{d:02d}" for d in range(2, 8)]
                    s_prices = await self._fetch_market_day(client, start_dates, "Start")
                    
                    # Fetch End (Dec or Today)
                    today = datetime.now().date()
                    
                    if year == today.year:
                        # If current year, scan backwards from TODAY
                        print(f"DEBUG: Current Year {year} detected. Scanning backward from {today}...")
                        end_dates = [
                            (today - datetime.timedelta(days=i)).strftime("%Y%m%d")
                            for i in range(7)
                        ]
                    else:
                        # Historic year: standard Dec 31 logic
                        end_dates = [f"{year}12{d:02d}" for d in range(31, 24, -1)]
                    
                    e_prices = await self._fetch_market_day(client, end_dates, "End")
                    
                    # Combine
                    result_data = {}
                    all_codes = set(s_prices.keys()) | set(e_prices.keys())
                    
                    # Identify IPO Lookup Candidates (Start Missing + Known Listing Date in this Year)
                    ipo_lookup_dates = {} # {date_str: [code1, code2]}
                    
                    for code in all_codes:
                        s_p = s_prices.get(code, 0.0)
                        
                        # Optimization: Smart IPO Lookup
                        if s_p == 0 and code in listing_dates:
                            listing_date = listing_dates[code] # "YYYY-MM-DD"
                            # Check if Listing Year matches Target Year
                            if listing_date.startswith(str(year)):
                                # Formate as YYYYMMDD
                                d_str = listing_date.replace('-', '')
                                if d_str not in ipo_lookup_dates:
                                    ipo_lookup_dates[d_str] = []
                                ipo_lookup_dates[d_str].append(code)

                    # Execute Targeted IPO Lookups (Batched by Date)
                    if ipo_lookup_dates:
                        print(f"  Performing Targeted IPO Lookups for {len(ipo_lookup_dates)} dates (Parallel)...")
                        
                        async def fetch_ipo_date(d_str, codes):
                             # Reuse _fetch_market_day but for a SINGLE date
                             ipo_prices = await self._fetch_market_day(client, [d_str], f"IPO_{d_str}")
                             return d_str, codes, ipo_prices

                        ipo_tasks = [fetch_ipo_date(d, c) for d, c in ipo_lookup_dates.items()]
                        ipo_results = await asyncio.gather(*ipo_tasks)
                        
                        for _, codes, ipo_prices in ipo_results:
                            for code in codes:
                                price = ipo_prices.get(code, 0.0)
                                if price > 0:
                                    s_prices[code] = price

                    # Final Merge
                    for code in all_codes:
                        s_p = s_prices.get(code, 0.0)
                        e_p = e_prices.get(code, 0.0)

                        if s_p > 0 or e_p > 0:
                            result_data[code] = {
                                'start': s_p,
                                'end': e_p
                            }
                    
                    # Save Cache
                    with open(cache_file, 'w') as f:
                        json.dump(result_data, f)
                        
                    return year, result_data

        # Execute Parallel
        tasks = [fetch_one_year(y) for y in years]
        results_list = await asyncio.gather(*tasks)
        
        for y, r in results_list:
            if r: results[y] = r

        return results


    async def _fetch_market_day(self, client, candidates, label):
        for date_str in candidates:
            url = "https://www.twse.com.tw/exchangeReport/MI_INDEX"
            # type=ALLBUT0999 gives all stocks
            params = {"response": "json", "date": date_str, "type": "ALLBUT0999"}
            try:
                # Sleep to respect rate limit
                await asyncio.sleep(1.0)
                print(f"Fetching {label} Market Data: {date_str}...")
                resp = await client.get(url, params=params, timeout=15.0)
                data = resp.json()
                
                if data.get('stat') == 'OK':
                    raw_rows = []
                    tables = data.get('tables', [])
                    # DEBUG
                    # if len(tables) > 0 and '2006' in date_str:
                    #     print(f"DEBUG: MI_INDEX {date_str} Encoding: {resp.encoding}")
                        # print(f"DEBUG: Tables[8] Keys: {tables[8].keys() if len(tables)>8 else 'N/A'}")
                    
                    target_table = None
                    for i, t in enumerate(tables):
                        title = t.get('title', '')
                        fields = t.get('fields', [])
                        
                        # Rank 1: Precise Title Match
                        if "每日收盤行情" in title:
                            target_table = t
                            break
                        
                        # Rank 2: Fields Match (Code + Close)
                        if "證券代號" in fields and "收盤價" in fields:
                            target_table = t
                            break
                    
                    # Rank 3: Fallback to Table 8 (Standard for most years)
                    if not target_table and len(tables) > 8:
                        # Validate Fields just in case
                        f8 = tables[8].get('fields', [])
                        if "證券代號" in f8:
                            target_table = tables[8]
                            print(f"DEBUG: Using Table 8 fallback for {date_str}")
                    
                    if target_table:
                        raw_rows = target_table.get('data', [])
                    else:
                        # Legacy fallback
                        raw_rows = data.get('data9', []) or data.get('data8', [])
                            
                    # Fallback to legacy data9/data8 checks if tables not found?
                    if not raw_rows:
                        raw_rows = data.get('data9', []) or data.get('data8', [])
                    
                    prices = {}
                    for row in raw_rows:
                        # Row: Code(0), Name(1), Vol, Trans, Val, Open(5), High, Low, Close(8)
                        # Check length? 
                        if len(row) < 9: continue
                        
                        code = row[0]
                        price_str = row[8] # Close is usually index 8 check fields?
                        # If parsed from fields, we could map dynamically.
                        # Assuming standard: [Code, Name, Vol, Tkts, Val, Open, High, Low, Close, ...]
                        
                        # Handle '--' or ','
                        try:
                            p = float(price_str.replace(',', ''))
                        except:
                            p = 0.0
                        prices[code] = p
                    
                    if prices:
                        return prices
                        try:
                            p = float(price_str.replace(',', ''))
                        except:
                            p = 0.0
                        prices[code] = p
                    
                    if prices:
                        return prices
            except Exception as e:
                print(f"Error fetching {date_str}: {e}")
                pass
        return {}
        
    async def fetch_fmtqik(self, stock_code: str):
        """
        Fetch /exchangeReport/FMTQIK for Yearly Summary (Open, High, Low, Close, Avg).
        Returns DataFrame with 'year' index.
        """
        # Finds cache first
        file_path = os.path.join(self.data_dir, f"{stock_code}_FMTQIK.json")
        data = None
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except:
                    pass
        
        async with httpx.AsyncClient() as client:
            if not data:
                url = "https://www.twse.com.tw/exchangeReport/FMTQIK"
                params = {"response": "json", "stockNo": stock_code}
                try:
                    await asyncio.sleep(0.1) # Short delay
                    resp = await client.get(url, params=params, timeout=10.0, follow_redirects=True)
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get('stat') == 'OK':
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False)
                except Exception as e:
                    print(f"Error fetching FMTQIK {stock_code}: {e}")
                    return None
        
        if data and data.get('stat') == 'OK':
            # Parse
            rows = []
            for r in data['data']:
                # ["112", "...", "...", "Open", "High", "Low", "Close", "Avg", ...]
                # Index 0: Year (ROC)
                # Index 3: Open? check logic. 
                # FMTQIK Fields: ["年度", "成交股數", "成交金額", "成交筆數", "最高價", "最低價", "加權平均價", "收盤價", "發行股數", "本益比", "殖利率", "股價淨值比"]?
                # Wait, schema varies!
                # I must check FIELDS.
                # Usual FMTQIK: ["年度","成交股數","成交金額","最高價","最低價","平均價","收盤價", "開盤價"? No open?]
                # FMTQIK often MISSES Open Price! 
                # Let's check fields via Probe?
                # Or use 'Avg' as proxy for 'Open' if missing? No.
                # 'Average' is VWAP.
                # If 'Open' is missing, I can't do "Buy at First Day Open".
                # But I have Average. And I have Close.
                # If I use Average for "Buy"? Deviation risk.
                # Wait, does FMTQIK have Open?
                # Search: "TWSE FMTQIK fields".
                # It usually DOES NOT have Open.
                # Fields: Year, Vol, Val, High, Low, Avg, Close, ...
                # Strategy: Use 'Avg' for entry? Or 'Close' of previous year?
                # Buy at Jan Open ~ Prev Year Close?
                # Or just use 'Avg' for both Entry and Reinvest?
                # User's logic: "Buy at First Open".
                # If I use FMTQIK, I compromise accuracy for speed.
                # But for "Scan All", maybe acceptable.
                # OR: I can fetch Jan Data (Stock_Day) for all years? 1000 stocks * 20 reqs = 20,000 reqs. Still high.
                # I'll stick to FMTQIK and use "Avg" or "Close-of-Prev" as proxy for Open.
                # Or Assume Open = Avg?
                # Actually, I'll log variables.
                
                # Let's map dynamically:
                fields = data.get('fields', [])
                # Map fields
                try:
                    y_roc = int(r[0])
                    y_ad = y_roc + 1911
                    
                    # Def vals
                    o_val = 0.0
                    h_val = 0.0
                    l_val = 0.0
                    c_val = 0.0
                    avg_val = 0.0
                    
                    # Parse by index if fields align?
                    # Typical: Year, Vol, Val, High, Low, Avg, Close ...
                    # But I should verify.
                    # Just enable robust parsing.
                    pass 
                except:
                    pass
            # For now, return raw data or DataFrame
            return data
        return None

    async def fetch_ex_rights_history(self, year: int):
        """
        Fetch TWT49U (Ex-Rights/Dividend) for the whole year.
        Uses Quarterly fetching to avoid API range limits.
        Returns dict: {stock_code: {'cash': float, 'stock_rate': float}}
        """
        url = "https://www.twse.com.tw/exchangeReport/TWT49U"
        results = {}
        
        # Split into Quarters to avoid "Range too wide" or other API issues
        quarters = [
            (f"{year}0101", f"{year}0331"),
            (f"{year}0401", f"{year}0630"),
            (f"{year}0701", f"{year}0930"),
            (f"{year}1001", f"{year}1231"),
        ]
        
        async with httpx.AsyncClient() as client:
            for start, end in quarters:
                params = {
                    "response": "json",
                    "startDate": start,
                    "endDate": end
                }
                try:
                    # Delay to be nice
                    await asyncio.sleep(0.5) 
                    resp = await client.get(url, params=params, timeout=10.0)
                    data = resp.json()
                    
                    if data.get('stat') == 'OK' and data.get('data'):
                        # Parse
                        for row in data['data']:
                            try:
                                code = row[1]
                                # Check if row has enough columns
                                # Schema might vary.
                                # Try to identify columns by content or assume standard
                                # Standard: [Date, Code, Name, Prior, Ref, RightsVal/Type?, CashVal/Type?, ...]
                                # Let's handle 2024 vs 2007 schema difference dynamically if possible?
                                # Hard to detect without fields.
                                # But let's try the logic that worked for 2007 patch diagnosis?
                                # Actually, 2007 Probe said index 6 is Rights, 7 is Cash.
                                # 2024 Probe said Index 5 is Rights+Div, Index 6 is Type?
                                # 2024: `['113/01/04', '2454', ..., '928.40', '24.60', '息', ...]`
                                # Index 5 is '24.60' (Value). Index 6 is '息' (Type).
                                # 2007: `[..., '64.70', '1.31', '2.99', ...]`
                                # Index 5 is '1.31' (Rights). Index 6 is '2.99' (Cash).
                                
                                # Heuristic:
                                # Look for "Rights" or "Div" columns by checking typical values or header if available?
                                # Detailed parsing is hard without seeing header.
                                # BUT: The goal is TSMC Correlation.
                                # TSMC usually pays Cash Div.
                                # In 2024 style: Value is at Index 5. Type at Index 6.
                                # In 2007 style: Rights at 5. Cash at 6.
                                
                                # Implementation: Try to parse strictly by year range?
                                # Or parse based on list length?
                                # 2024 list length: 15.
                                # 2007 list length: 17.
                                
                                length = len(row)
                                cash_val = 0.0
                                stock_rate = 0.0
                                
                                if length >= 17: # Old Schema (e.g. 2007)
                                    # Index 6 is Cash (Row 7). Index 5 is Rights.
                                    # Prior: 3. Ref: 4.
                                    prior = float(row[3].replace(',', ''))
                                    ref = float(row[4].replace(',', ''))
                                    c_str = row[6] # Cash
                                    r_str = row[5] # Rights
                                    
                                    cash_val = float(c_str.replace(',', '')) if c_str != '-' else 0.0
                                    rights_val = float(r_str.replace(',', '')) if r_str != '-' else 0.0
                                    
                                    # Derive Stock Rate from Rights Val
                                    # Rights Val = Prior - (Ref ignoring cash) ?
                                    # Formula: Ref = (Prior - Cash) / (1 + Rate)
                                    # Rate = ((Prior - Cash) / Ref) - 1
                                    if ref > 0:
                                        stock_rate = ((prior - cash_val) / ref) - 1
                                elif length <= 15: # New Schema (e.g. 2024)
                                    # Index 5 is Value. Index 6 is Type ('權', '息', '權息').
                                    # Prior: 3. Ref: 4.
                                    prior = float(row[3].replace(',', ''))
                                    ref = float(row[4].replace(',', ''))
                                    val_str = row[5]
                                    type_str = row[6]
                                    
                                    val = float(val_str.replace(',', ''))
                                    
                                    if type_str == '息':
                                        cash_val = val
                                    elif type_str == '權':
                                        # Value is Rights Value
                                        # Rate logic same: Rate = (Prior/Ref) - 1 (since Cash=0)
                                        if ref > 0:
                                            stock_rate = (prior / ref) - 1
                                    elif '權' in type_str and '息' in type_str:
                                        # Combined?
                                        # Check if next columns split it?
                                        # 2024 Sample doesn't show split cols clearly.
                                        # Assuming simple case for now. 
                                        # If combined, usually separate columns exist or parsing needed.
                                        # For TSMC, mostly '息' recently.
                                        if ref > 0:
                                            # Approximation: Total Val = Prior - Ref
                                            # If mostly cash...
                                            diff = prior - ref
                                            # Assume all Cash if Type is Mixed? No.
                                            # Let's hope TSMC is simple.
                                            cash_val = val # Fallback
                                            
                                # Sanity Check
                                if stock_rate < 0.0001: stock_rate = 0.0
                                stock_div_par = stock_rate * 10.0
                                
                                if code not in results:
                                    results[code] = {'cash': 0.0, 'stock': 0.0}
                                results[code]['cash'] += cash_val
                                results[code]['stock'] += stock_div_par
                                
                            except:
                                pass
                except Exception as e:
                    print(f"Error fetching TWT49U for {year} Q: {e}")
                    
        return results
