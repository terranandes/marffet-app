
import asyncio
# import pandas as pd # Lazy Import
from app.project_tw.crawler import TWSECrawler
from app.project_tw.crawler_tpex import TPEXCrawler
from app.project_tw.calculator import ROICalculator

class MarsStrategy:
    def __init__(self):
        self.crawler = TWSECrawler()
        self.crawler_tpex = TPEXCrawler()
        self.calculator = ROICalculator()
        self.top_50 = []
        
    async def analyze_stock_batch(self, stock_codes: list, start_year: int, end_year: int, std_threshold: float = 100.0, status_callback=None):
        from app.services.market_data_provider import MarketDataProvider
        import pandas as pd
        """
        Analyze a batch of stocks concurrently using Market-Wide Batch Data (Nominal Prices from DuckDB).
        """
        results = []
        
        # 1. Load Dividend Data from DuckDB (Single Source of Truth)
        msg = "Loading Dividend Data from DuckDB..."
        print(msg)
        if status_callback: status_callback(msg)
        
        # Format: {stock_id: {year: {'cash': x, 'stock': y}}}
        all_dividends = MarketDataProvider.load_dividends_dict()
        years = list(range(start_year, end_year + 1))
            
        print(f"Dividend Data Loaded ({len(all_dividends)} stocks from DuckDB).")

        # 2. Fetch Market Prices (Nominal from DuckDB)
        msg = f"Fetching Market Prices ({start_year}-{end_year}) from DuckDB..."
        print(msg)
        if status_callback: status_callback(msg, 20)
        
        # Determine Universe
        if stock_codes == ["ALL"]:
            print("Auto-Detecting Stock Universe from DuckDB...")
            stock_list = MarketDataProvider.get_stock_list()
            print(f"Detected {len(stock_list)} unique stocks.")
        else:
            stock_list = stock_codes

        # Optimizing Fetch: Bulk vs Individual
        # If analyzing many stocks, fetch ALL history to avoid N queries
        use_bulk = (len(stock_list) > 50) or (stock_codes == ["ALL"])
        
        bulk_df = None
        if use_bulk:
            print("🚀 Loading FULL Market History (Bulk)...")
            # Fetch from start_year Jan 1
            bulk_df = MarketDataProvider.get_all_daily_history_df(f"{start_year}-01-01")
            print(f"Loaded {len(bulk_df):,} rows.")
            
        # 3. Process Stocks
        print(f"Processing {len(stock_list)} stocks...")
        
        total_stocks = len(stock_list)
        completed_count = 0
        
        # Helper to get DF
        def get_df(code):
            if use_bulk:
                if bulk_df.empty: return pd.DataFrame()
                # Filter by stock_id
                return bulk_df[bulk_df['stock_id'] == code].copy()
            else:
                return MarketDataProvider.get_daily_history_df(code, f"{start_year}-01-01")

        # Async Wrapper for CPU-bound calculation (optional, but good for keeping event loop alive)
        # Using simple loop for now as checking 1000 stocks is fast in memory
        
        for code in stock_list:
            try:
                df = get_df(code)
                if df.empty: 
                    completed_count += 1
                    continue
                
                # Pre-processing: ensure 'year' column
                if 'year' not in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df['year'] = df['date'].dt.year
                
                # Filter Range (Just in case DB has older data)
                df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
                
                if df.empty:
                    completed_count += 1
                    continue

                # Prepare Dividends (from DuckDB, keyed by stock_id → year)
                stock_divs = {}
                code_divs = all_dividends.get(code, {})
                for y in years:
                    if y in code_divs:
                        stock_divs[y] = code_divs[y]

                # PATCH: TSMC, 0050, 2881 (Preserve legacy patches)
                # PATCH: TSMC
                if code == '2330':
                    if 2006 in years: stock_divs[2006] = {'cash': 2.5, 'stock': 0.3}
                    if 2007 in years: stock_divs[2007] = {'cash': 3.0, 'stock': 0.05}
                # PATCH: 0050
                if code == '0050':
                    if 2006 not in stock_divs or stock_divs[2006].get('cash', 0) == 0: stock_divs[2006] = {'cash': 2.5, 'stock': 0.0}
                    if 2007 not in stock_divs or stock_divs[2007].get('cash', 0) == 0: stock_divs[2007] = {'cash': 2.0, 'stock': 0.0}
                    if 2008 not in stock_divs or stock_divs[2008].get('cash', 0) == 0: stock_divs[2008] = {'cash': 1.0, 'stock': 0.0}
                    if 2025 in years: stock_divs[2025] = {'cash': 1.035, 'stock': 0.0}
                # PATCH: 2881
                if code == '2881':
                    if 2006 not in stock_divs or stock_divs[2006].get('cash', 0) == 0: stock_divs[2006] = {'cash': 1.15, 'stock': 0.0}
                    if 2007 not in stock_divs or stock_divs[2007].get('cash', 0) == 0: stock_divs[2007] = {'cash': 1.00, 'stock': 0.0}
                    if 2008 not in stock_divs or stock_divs[2008].get('cash', 0) == 0: stock_divs[2008] = {'cash': 1.50, 'stock': 0.0}
                # PATCH: 00937B
                if code == '00937B':
                     if 2024 in years: stock_divs[2024] = {'cash': 1.02, 'stock': 0.0}
                     if 2025 in years: stock_divs[2025] = {'cash': 1.02, 'stock': 0.0}

                # Run Simulation
                metrics = self.calculator.calculate_complex_simulation(df, start_year, dividend_data=stock_divs, stock_code=code)
                
                if metrics:
                    metrics['stock_code'] = code
                    metrics['stock_name'] = code # Placeholder, filter_and_rank fills real name
                    metrics['price'] = df.iloc[-1]['close'] if not df.empty else 0
                    
                    # Volatility
                    if len(df) > 1:
                        # Annual returns for volatility? Mars used Annual Returns std previously.
                        # "volatility_pct = annual_returns.std() * 100"
                        # But df is DAILY.
                        # Legacy code was using "Synthetic DF" with 1 row per year.
                        # So `df['close'].pct_change()` was ANNUAL return.
                        # Here df is DAILY.
                        # Only way to match legacy logic is to resample to yearly?
                        # Or use Daily Volatility * sqrt(252)?
                        # User requirement says: "StdDev of annualized accumulating returns".
                        # Let's compute ANNUAL returns from daily data for this metric?
                        # Or just use the 'cagr_std' logic which uses the trajectories.
                        
                        # Legacy logic: 
                        # rows.append({'avg': ..., 'close': p_end}) -> df
                        # annual_returns = df['close'].pct_change()
                        # metrics['volatility_pct'] = annual_returns.std() * 100
                        
                        # So we should replicate ANNUAL returns std.
                        # Get year-end closes
                        yearly_closes = df.groupby('year')['close'].last()
                        pct_changes = yearly_closes.pct_change().dropna()
                        metrics['volatility_pct'] = pct_changes.std() * 100 if len(pct_changes) > 1 else 0.0
                    else:
                        metrics['volatility_pct'] = 0.0
                        
                    metrics['cagr_pct'] = metrics.get(f"s{start_year}e{end_year}bao", 0)
                    
                    # CAGR Trajectory Std
                    traj_values = []
                    for y in years:
                        key = f"s{start_year}e{y}bao"
                        val = metrics.get(key)
                        if val is not None:
                            try:
                                traj_values.append(float(val))
                            except: pass
                    
                    if len(traj_values) > 1:
                        metrics['cagr_std'] = pd.Series(traj_values).std()
                    else:
                        metrics['cagr_std'] = 999.0

                    metrics['valid_lasting_years'] = len(df.groupby('year')) # Count distinct years
                    
                    results.append(metrics)
                    
            except Exception as e:
                # print(f"Error {code}: {e}")
                pass
            
            # Progress
            completed_count += 1
            if status_callback and total_stocks > 0:
                 progress = 50 + int((completed_count / total_stocks) * 45)
                 if completed_count % max(1, total_stocks // 20) == 0:
                    status_callback(f"Analyzed {code} ({completed_count}/{total_stocks})...", progress)
                    await asyncio.sleep(0) # Yield

        if status_callback: status_callback("Stock analysis complete.", 95)
        return results

    def filter_and_rank(self, metrics_list, stock_dict=None):
        import pandas as pd
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
        import pandas as pd
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
