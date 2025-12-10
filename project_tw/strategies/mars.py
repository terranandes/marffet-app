
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
        
    async def analyze_stock_batch(self, stock_codes: list, start_year: int, end_year: int, std_threshold: float = 100.0):
        """
        Analyze a batch of stocks concurrently using Market-Wide Batch Data.
        """
        results = []
        
        # 1. Pre-fetch Dividend Data (TWT49U) - Efficient (Annual Queries)
        print("Fetching Dividend Data (TWSE TWT49U)...")
        dividend_data = {} # {year: {code: {'cash': x, 'stock': y}}}
        years = list(range(start_year, end_year + 1))
        
        # Use simple loops for pre-fetching to ensure stability
        for y in years:
             data = await self.crawler.fetch_ex_rights_history(y)
             # TPEx Dividends (Future)
             tpex_div = await self.crawler_tpex.fetch_ex_rights_history(y, y) # Start/End same year
             if tpex_div:
                 data.update(tpex_div)
                 
             dividend_data[y] = data
        print("Dividend Data Fetched.")

        # 2. Pre-fetch Market Prices (Start Jan / End Dec) - Efficient (~40 calls total)
        print("Fetching Market Prices (TWSE + TPEx) in Parallel...")
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
        print(f"Processing {len(stock_codes)} stocks...")
        
        for code in stock_codes:
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
                     continue
                     
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
                    metrics['stock_name'] = code # Placeholder, run_analysis will join name
                    metrics['price'] = df.iloc[-1]['close']
                    metrics['volatility_pct'] = 0.0 # No daily vol in scan mode
                    metrics['cagr_pct'] = metrics.get(f"s{start_year}e{end_year}bao", 0)
                    results.append(metrics)
                    
            except Exception as e:
                # print(f"Err {code}: {e}")
                pass

        return results

    def filter_and_rank(self, metrics_list, std_threshold=100.0):
        """
        Apply Mars logic:
        1. Low Volatility (std < threshold)
        2. Stable Growth (Rank by CAGR)
        """
        df = pd.DataFrame(metrics_list)
        if df.empty:
            return []
            
        # Filter
        qualified = df[df['volatility_pct'] <= std_threshold]
        
        # Rank desc by CAGR
        ranked = qualified.sort_values(by='cagr_pct', ascending=False)
        
        # Take Top 50
        # CRITICAL: Replace NaN with None (or 0) to avoid JSON serialization errors
        ranked = ranked.fillna(0) # Or replace np.nan with None if preferred
        self.top_50 = ranked.head(50).to_dict('records')
        return self.top_50

    def save_to_excel(self, output_path: str):
        """
        Save the filtered Top 50 results to an Excel file.
        Matches the user's requested output format (approx).
        """
        if not self.top_50:
            print("No data to save.")
            return

        df = pd.DataFrame(self.top_50)
        # Reorder columns if needed for readability
        # Align with Legacy Format: id, name, id_name_yrs, s...bao
        df = df.rename(columns={'stock_code': 'id', 'stock_name': 'name'})
        
        # Create id_name_yrs
        # Try to find duration column
        yrs_col = [c for c in df.columns if c.endswith('yrs')]
        yrs_val = df[yrs_col[0]] if yrs_col else 0
        df['id_name_yrs'] = df['id'].astype(str) + '_' + df['name'] + '_' + yrs_val.astype(str)
        
        # Reorder
        base_cols = ['id', 'name', 'id_name_yrs', 'price', 'cagr_pct', 'volatility_pct']
        
        # Identify dynamic Yearly columns (s...bao)
        all_cols = df.columns.tolist()
        yearly_cols = sorted([c for c in all_cols if c.startswith('s') and 'bao' in c])
        # Also keep s...yrs
        yrs_cols = sorted([c for c in all_cols if c.endswith('yrs')])
        
        other_cols = [c for c in all_cols if c not in base_cols and c not in yearly_cols and c not in yrs_cols]
        
        final_cols = base_cols + yearly_cols + yrs_cols + other_cols
        
        # Filter only existing columns
        final_cols = [c for c in final_cols if c in df.columns]
        
        df = df[final_cols]
        
        print(f"Saving filtered list to {output_path}...")
        df.to_excel(output_path, index=False)
        print("Save complete.")
