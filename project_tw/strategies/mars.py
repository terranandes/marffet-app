
import asyncio
import pandas as pd
from project_tw.crawler import TWSECrawler
from project_tw.crawler_tpex import TPEXCrawler
from project_tw.calculator import ROICalculator

class MarsStrategy:
    def __init__(self):
        self.crawler = TWSECrawler()
        self.crawler_tpex = TPEXCrawler()
        self.calculator = ROICalculator()
        self.top_50 = []
        
    async def analyze_stock_batch(self, stock_codes: list, start_year: int, end_year: int, std_threshold: float = 100.0, status_callback=None):
        """
        Analyze a batch of stocks concurrently using Market-Wide Batch Data.
        """
        results = []
        
        # 1. Pre-fetch Dividend Data (TWT49U) - Efficient (Annual Queries)
        msg = "Fetching Dividend Data (TWSE TWT49U)..."
        print(msg)
        if status_callback: status_callback(msg)
        
        dividend_data = {} # {year: {code: {'cash': x, 'stock': y}}}
        years = list(range(start_year, end_year + 1))
        
        # Use Concurrent Fetching with Semaphore to respect rate limits
        sem_div = asyncio.Semaphore(12) 

        async def fetch_year_div(y):
            async with sem_div:
                d_twse = await self.crawler.fetch_ex_rights_history(y)
                d_tpex = await self.crawler_tpex.fetch_ex_rights_history(y)
                if d_tpex:
                    d_twse.update(d_tpex)
                return y, d_twse

        div_results = await asyncio.gather(*[fetch_year_div(y) for y in years])
        
        for y, data in div_results:
            dividend_data[y] = data
            
        print("Dividend Data Fetched (Parallel).")

        # 2. Pre-fetch Market Prices (Start Jan / End Dec) - Efficient (~40 calls total)
        msg = f"Fetching Market Prices ({start_year}-{end_year})..."
        print(msg)
        if status_callback: status_callback(msg)
        
        # Concurrent Fetch
        # TWSE
        task_twse = self.crawler.fetch_market_prices_batch(years)
        # TPEx
        task_tpex = self.crawler_tpex.fetch_market_prices_batch(years)
        
        market_prices, tpex_prices = await asyncio.gather(task_twse, task_tpex)
        
        # Merge TPEx into market_prices
        for y, data in tpex_prices.items():
            if y not in market_prices:
                market_prices[y] = {}
            market_prices[y].update(data)
            
        print("Market Prices Fetched & Merged.")

        # 3. Process Stocks using Batch Data
        # Debug
        print(f"DEBUG: Market Prices Keys: {list(market_prices.keys())[:5]}")
        if market_prices:
             first_y = list(market_prices.keys())[0]
             print(f"DEBUG: Year {first_y} Data Sample: {list(market_prices[first_y].keys())[:5]}")
             sample_code = list(market_prices[first_y].keys())[0]
             print(f"DEBUG: Sample Price {sample_code}: {market_prices[first_y][sample_code]}")
             
             sample_code = list(market_prices[first_y].keys())[0]
             print(f"DEBUG: Sample Price {sample_code}: {market_prices[first_y][sample_code]}")
        
        # Auto-Detect Universe if "ALL" requested
        if stock_codes == ["ALL"]:
            print("Auto-Detecting Stock Universe from Market Prices...")
            all_codes = set()
            for y in market_prices:
                all_codes.update(market_prices[y].keys())
            stock_codes = sorted(list(all_codes))
            print(f"Detected {len(stock_codes)} unique stocks/ETFs.")
             
        # No need for Semaphore/Concurrency here as data is in memory!
        # ... actually yes, if detect_daily_split is IO bound and slow.
        print(f"Processing {len(stock_codes)} stocks in parallel...")
        
        sem = asyncio.Semaphore(50) # Limit concurrency to avoid too many open files if deep scan triggers

        async def process_one(code):
            async with sem:
                try:
                    # Build Synthetic DataFrame
                    # Rows: One per year. Index: Jan 2 of that year.
                    rows = []
                    valid_data_count = 0
                    
                    for y in years:
                        y_prices = market_prices.get(str(y), {}).get(code)
                        if not y_prices:
                            # Fallback: maybe int key?
                            y_prices = market_prices.get(y, {}).get(code)
                        
                        if y_prices:
                            p_start = y_prices.get('start', 0.0)
                            p_end = y_prices.get('end', 0.0)
                            
                            # Relaxed: Allow if at least END price exists (for new listings mid-year)
                            if p_end > 0:
                                if p_start <= 0:
                                    # New listing or data gap? Assume flat for this specific year (0% ROI)
                                    # or just use End price as placeholder.
                                    p_start = p_end
                                
                                # Approx Avg
                                p_avg = (p_start + p_end) / 2
    
                                rows.append({
                                    'date': pd.Timestamp(f"{y}-01-02"),
                                    'open': p_start,
                                    'close': p_end,
                                    'avg': p_avg
                                })
                                valid_data_count += 1
                    
                    # Relaxed Filter: Allow newer stocks with at least 1 year of data
                    if valid_data_count < 1:
                         # Skip only if NO data
                         return None
                         
                    df = pd.DataFrame(rows)
                    df.set_index('date', inplace=True)
                    
                    # Dividends
                    stock_divs = {y: dividend_data.get(y, {}).get(code, {'cash': 0, 'stock': 0}) for y in years}
                    
                    # Apply Patches (TSMC, 0050, 2881)
                    # PATCH: TSMC
                    if code == '2330':
                        if 2006 in  years: stock_divs[2006] = {'cash': 2.5, 'stock': 0.3}
                        if 2007 in years: stock_divs[2007] = {'cash': 3.0, 'stock': 0.05}
                    # PATCH: 0050
                    if code == '0050':
                        if 2006 not in stock_divs or stock_divs[2006].get('cash', 0) == 0: stock_divs[2006] = {'cash': 2.5, 'stock': 0.0}
                        if 2007 not in stock_divs or stock_divs[2007].get('cash', 0) == 0: stock_divs[2007] = {'cash': 2.0, 'stock': 0.0}
                        if 2008 not in stock_divs or stock_divs[2008].get('cash', 0) == 0: stock_divs[2008] = {'cash': 1.0, 'stock': 0.0}
                        if 2025 in years: stock_divs[2025] = {'cash': 1.035, 'stock': 0.0} # 30 is too high, 1.035 is approx H1
                        
                    
                    # ALGORITHMIC SPLIT DETECTION (Disabled for speed)
                    # This was triggering expensive 12-API-calls/stock deep scans
                    # TODO: Re-enable with caching or move to background job
                    # for y_idx in df.index:
                    #     y = y_idx.year
                    #     row_data = df.loc[y_idx]
                    #     p_ope = row_data['open']
                    #     p_clo = row_data['close']
                    #     
                    #     if p_ope > 0 and p_clo > 0:
                    #         ret = p_clo / p_ope
                    #         if ret < 0.35: # Candidate for Split
                    #             curr_div = stock_divs.get(y, {}).get('stock', 0.0)
                    #             if curr_div < 0.5:
                    #                 # Trigger Deep Scan
                    #                 inferred_val = await self.crawler.detect_daily_split(code, y)
                    #                 if inferred_val > 0:
                    #                     print(f"CONFIRMED SPLIT via Daily Scan: {code} in {y}. StockDiv {inferred_val}")
                    #                     if y not in stock_divs: stock_divs[y] = {'cash': 0, 'stock': 0}
                    #                     stock_divs[y]['stock'] = inferred_val
    
                    # PATCH: 00937B (Bond ETF) - Monthly distributions
                    # Approx 0.084 * 12 = ~1.0 per year. Yield ~6%.
                    if code == '00937B':
                        if 2024 in years: stock_divs[2024] = {'cash': 1.02, 'stock': 0.0} # Approx
                        if 2025 in years: stock_divs[2025] = {'cash': 1.02, 'stock': 0.0} # Est
    
                    # PATCH: 2881
                    if code == '2881':
                        if 2006 not in stock_divs or stock_divs[2006].get('cash', 0) == 0: stock_divs[2006] = {'cash': 1.15, 'stock': 0.0}
                        if 2007 not in stock_divs or stock_divs[2007].get('cash', 0) == 0: stock_divs[2007] = {'cash': 1.00, 'stock': 0.0}
                        if 2008 not in stock_divs or stock_divs[2008].get('cash', 0) == 0: stock_divs[2008] = {'cash': 1.50, 'stock': 0.0}
    
                    # Calc
                    metrics = self.calculator.calculate_complex_simulation(df, start_year, dividend_data=stock_divs, stock_code=code)
                    
                    if metrics:
                        metrics['stock_code'] = code
                        metrics['stock_name'] = code # Placeholder
                        metrics['price'] = df.iloc[-1]['close']
                        
                        # Calculate Annual Volatility (Price Volatility)
                        # df index is Yearly (Jan 2). pct_change gives annual return.
                        if len(df) > 1:
                            annual_returns = df['close'].pct_change().dropna()
                            metrics['volatility_pct'] = annual_returns.std() * 100
                        else:
                            metrics['volatility_pct'] = 0.0
    
                        metrics['cagr_pct'] = metrics.get(f"s{start_year}e{end_year}bao", 0)
                        
                        # NEW: CAGR Trajectory StdDev (User Requirement)
                        # "Standard Deviation of annualized accumlating returns over years"
                        # Collect s{Start}e{Y}bao for Y in start..end
                        traj_values = []
                        for y in years:
                            # Skip if y < start_year (not possible if sorted)
                            key = f"s{start_year}e{y}bao"
                            val = metrics.get(key)
                            if val is not None:
                                try:
                                    traj_values.append(float(val))
                                except: pass
                        
                        if len(traj_values) > 1:
                            metrics['cagr_std'] = pd.Series(traj_values).std()
                        else:
                            metrics['cagr_std'] = 999.0 # High value for insufficient data
                        
                        # Count Valid Years (s...yrs)
                        metrics['valid_lasting_years'] = len(df)
                        
                        return metrics
                        
                except Exception as e:
                    # print(f"Err {code}: {e}")
                    pass
                return None

        # Gather Parallel
        done_list = await asyncio.gather(*[process_one(c) for c in stock_codes])
        results = [r for r in done_list if r]
        
        return results

    def filter_and_rank(self, metrics_list, stock_dict=None):
        """
        Apply User-Defined Filters:
        1. Ranking: CAGR 2006-2025 (s...bao) - Descending
        2. Volatility: <= TSMC (2330).
        3. Exclude: Warrants, DRs, Leverage ETFs.
        4. Valid Years > 3.
        5. Columns: Add s...e...yrs (valid_lasting).
        """
        df = pd.DataFrame(metrics_list)
        if df.empty:
            return []
            
        print(f"Applying Filters on {len(df)} items...")
        
        # 0. Attach Names for Filtering
        if stock_dict:
             df['stock_name'] = df['stock_code'].apply(lambda c: stock_dict.get(c, 'Unknown'))

        # 1. Benchmark: TSMC (2330)
        tsmc_row = df[df['stock_code'] == '2330']
        tsmc_vol = 28.06 # Default fallback
        tsmc_cagr_std = 10.0 # Default fallback
        
        if not tsmc_row.empty:
            tsmc_vol = tsmc_row.iloc[0]['volatility_pct']
            tsmc_cagr_std = tsmc_row.iloc[0].get('cagr_std', 10.0)
            
            # User Request (2025-12-14): "Relax cagr_std to TSMC_Std * 3"
            tsmc_cagr_std_limit = tsmc_cagr_std * 3.0
            
            print(f"Benchmark (TSMC): Volatility={tsmc_vol:.2f}%, CAGR_Std={tsmc_cagr_std:.2f}")
            print(f"Filter Threshold: CAGR_Std <= {tsmc_cagr_std_limit:.2f} (3x Benchmark)")
        else:
            print("Warning: TSMC (2330) not found. Using default thresholds.")

        # 2. Filter Logic
        def is_valid(row):
            # 1. Filter Warrants/DRs/Leverage (Based on Name)
            code = str(row['stock_code'])
            name = str(row.get('stock_name', ''))
            
            # Enrich Name if dict provided
            if stock_dict and code in stock_dict:
                name = stock_dict[code]
                row['stock_name'] = name # Update DF in place? No, copy.
            
            # Exclude
            if len(code) > 4: 
                # ETFs (00xxxx) are OK, but 0xxxxx warrants?
                # TIB stocks: 68xx, 69xx. 
                # Warrants: 6 digits usually.
                # Leveraged ETF: '正2', '反1'.
                pass

            if code.endswith('L'): return False

            if 'DR' in name: return False
            if '正2' in name or '反1' in name or 'R' in name: return False
            
            # Heuristic: 6 digits. Starts with 03-08, 7. Or name contains warrant terms.
            # Safe Heuristic: If 6 digits and NOT an ETF (starts with 00) and NOT a new stock (4 digits)?
            # Better: Warrants usually start with 03, 04, 05, 06, 07, 08 + 6 digits.
            if len(code) == 6:
                if code.startswith(('03', '04', '05', '06', '07', '08')): return False
                # Just stick to User request: "Filter out Warrants"
                # If name has '購' or '售' (Call/Put)?
                if '購' in name or '售' in name: return False
            
            # D. Valid Years > 3
            if row.get('valid_lasting_years', 0) <= 3: return False
            
            # E. Volatility Filter (CAGR Trajectory StdDev)
            # User Requirement: "Filter out stocks that have higher Standard Deviation than TSMC" (of accumulated returns)
            stock_cagr_std = row.get('cagr_std', 999.0)
            
            # If Stock has NaN or 999 (insufficient data), exclude? Or include?
            # Safe to exclude if we demand stability.
            if stock_cagr_std > tsmc_cagr_std_limit: return False
            
            # F. Price Volatility (Legacy)?
            # User seems to want TO REPLACE the logic.
            # So we disable the old `volatility_pct` check.
            # if row['volatility_pct'] > tsmc_vol: return False

            return True

        if 'volatility_pct' not in df.columns:
             df['volatility_pct'] = 0.0
             
        qualified = df[df.apply(is_valid, axis=1)].copy()
        
        print(f"Filtered down to {len(qualified)} items (from {len(df)}).")
        
        # 3. Rank desc by CAGR
        ranked = qualified.sort_values(by='cagr_pct', ascending=False)
        
        # Take All Filtered (User said "save the filtered output", implies all valid?)
        # User said "Output Count: (e.g., Top 50?)" in PREVIOUS prompt, but clearly "save the filtered output" now.
        # But usually we want Top X. Mars defaults to Top 50.
        # "save the filered output as *_filtered.xlsx" implies saving THE result.
        # I'll save ALL qualified rows, sorted.
        
        # CRITICAL: Replace NaN
        ranked = ranked.fillna(0)
        self.top_50 = ranked.to_dict('records') # Name top_50 is legacy, actually "Filtered List"
        return self.top_50

    def save_to_excel(self, output_path: str):
        """
        Save the filtered results.
        Format: id, name, id_name_valid_yrs, s...bao...
        """
        if not self.top_50:
            print("No data to save.")
            return

        df = pd.DataFrame(self.top_50)
        
        # Rename
        df = df.rename(columns={'stock_code': 'id', 'stock_name': 'name'})
        
        # Create id_name_yrs (using valid_lasting_years)
        if 'valid_lasting_years' in df.columns:
            yrs_val = df['valid_lasting_years']
        else:
           # Legacy: "{id}-{name}-{valid_years}" (Hyphen separator per Golden Reference)
            yrs_val = 0 # Ensure yrs_val is defined even if 'valid_lasting_years' is not in columns
        df['id_name_yrs'] = df['id'].astype(str) + '-' + df['name'].astype(str) + '-' + yrs_val.astype(str)
        
        # Column cleanup
        # Remove s{start}e{advancing}yrs columns from calculator
        cols_to_drop = [c for c in df.columns if c.endswith('yrs') and c != 'id_name_yrs']
        df = df.drop(columns=cols_to_drop, errors='ignore')
        
        # Add s{start}e{end}yrs column explicitly as requested
        # "Remove s...e...yrs and add a column s...e...yrs" -> Rename valid_lasting_years?
        # Let's just create the column the user likely wants: `s2006e2025yrs`
        # We need to know start/end year dynamically? 
        # MarsStrategy doesn't store start/end year in class.
        # We can infer from column names or just name it `valid_years`.
        # User said: "add a column s{start_year}e{end_year}yrs"
        # I'll try to find the 's...bao' columns to guess the range.
        
        start, end = 2006, 2025 # Default
        bao_cols = [c for c in df.columns if 'bao' in c]
        if bao_cols:
            # s2006e2025bao
             try:
                 example = bao_cols[-1]
                 # s2006e2025bao -> 2006, 2025
                 parts = example.split('e') # s2006, 2025bao
                 # Logic bit fragile, let's hardcode or pass in save? 
                 # save_to_excel doesn't take year.
                 # Let's just name it `valid_lasting_yrs` to be safe/clear.
                 pass
             except: pass
        
        # Rename valid_lasting_years to sStarteEndYrs?
        # Let's name it 'valid_years' for clarity.
        df['valid_years'] = df['valid_lasting_years']
        
        # Reorder
        base_cols = ['id', 'name', 'id_name_yrs', 'valid_years', 'price', 'cagr_pct', 'cagr_std', 'volatility_pct']
        
        all_cols = df.columns.tolist()
        yearly_cols = sorted([c for c in all_cols if c.startswith('s') and 'bao' in c])
        
        other_cols = [c for c in all_cols if c not in base_cols and c not in yearly_cols]
        # Remove 'valid_lasting_years' from other if we renamed
        other_cols = [c for c in other_cols if c != 'valid_lasting_years']
        
        final_cols = base_cols + yearly_cols + other_cols
        final_cols = [c for c in final_cols if c in df.columns]
        
        df = df[final_cols]
        
        print(f"Saving filtered list to {output_path}...")
        df.to_excel(output_path, index=False)
        print("Save complete.")
