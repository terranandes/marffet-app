# import pandas as pd # Lazy Import
# import numpy as np # Lazy Import
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from io import BytesIO
from datetime import datetime

# Import existing Services/Crawlers
from app.services.market_data_provider import MarketDataProvider
from app.services.roi_calculator import ROICalculator
from app.project_tw.crawler_cb import CBCrawler

# Setup Logging
logger = logging.getLogger(__name__)

def sanitize_numpy(obj):
    if isinstance(obj, dict):
        return {k: sanitize_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_numpy(v) for v in obj]
    elif hasattr(obj, 'item'):
        return obj.item()
    return obj

class MarsStrategy:
    def __init__(self):
        self.calculator = ROICalculator()
        self.data_dir = Path("data/raw")
        self.top_50 = []
        # Dividends are now fetched from MarketDataProvider (DuckDB)

    async def analyze(self, stock_ids: List[str], start_year: int = 2006, principal: float = 1_000_000, contribution: float = 60_000) -> List[Dict[str, Any]]:
        import numpy as np
        """
        Analyze stocks using bulk data loading for high performance.
        """
        start_time = datetime.now()
        
        # 1. Detect Universe
        if not stock_ids or stock_ids == ["ALL"]:
            stock_ids = MarketDataProvider.get_stock_list()
            if not stock_ids:
                logger.warning("DuckDB is empty. Cannot auto-detect stocks.")
                return []
            is_full_universe = True
        else:
            is_full_universe = False

        # 2. Bulk Fetch Data (Memory-Safe Chunked Optimization)
        logger.info(f"Loading market data in memory-safe chunks for {len(stock_ids)} stocks...")
        start_date = f"{start_year}-01-01"
        
        # Dividends are extremely lightweight (~30k rows), fetching all is safe
        all_dividends_df = MarketDataProvider.get_all_dividends_df(start_year)
        if hasattr(all_dividends_df, 'groupby'):
            div_groups = all_dividends_df.groupby('stock_id')
        else:
            div_groups = {}

        # 3. Load patches once
        if not hasattr(self, 'dividend_patches'):
            try:
                patch_file = self.data_dir.parent / "dividend_patches.json"
                if patch_file.exists():
                    with open(patch_file, 'r') as f:
                        self.dividend_patches = json.load(f)
                else:
                    self.dividend_patches = {}
            except Exception as e:
                logger.error(f"Error loading dividend patches: {e}")
                self.dividend_patches = {}

        # 4 & 5 & 6. Setup Iteration across DuckDB in Chunks of 200 stocks (~40MB RAM max)
        results = []
        end_year = datetime.now().year
        years = list(range(start_year, end_year + 1))
        
        from app.services.market_db import get_connection
        conn = get_connection(read_only=True)
        chunk_size = 200
        processed_count = 0
        total_stocks = len(stock_ids)
        
        logger.info(f"Processing {total_stocks} stocks in chunks of {chunk_size}...")
        
        try:
            for i in range(0, total_stocks, chunk_size):
                chunk = stock_ids[i:i+chunk_size]
                
                # Fetch price chunk directly from DuckDB (avoid holding 500MB globally)
                q = f"SELECT stock_id, date, open, high, low, close, volume FROM daily_prices WHERE stock_id IN ({','.join(['?']*len(chunk))}) AND date >= ? ORDER BY stock_id, date ASC"
                params = chunk + [start_date]
                chunk_df = conn.execute(q, params).df()
                
                if chunk_df.empty:
                    continue
                    
                chunk_df['year'] = chunk_df['date'].dt.year
                
                # Pre-calculate yearly stats for this specific chunk (saves massive groupby time)
                yearly_agg = chunk_df.groupby(['stock_id', 'year']).agg(
                    action_price=('open', 'first'),
                    avg_price=('close', 'mean'),
                    end_price=('close', 'last')
                ).reset_index()
                
                yearly_agg_groups = yearly_agg.groupby('stock_id')
                price_groups = chunk_df.groupby('stock_id')
                
                # Process each stock in the current chunk
                for code in chunk:
                    if code not in price_groups.groups: continue
                    df_group = price_groups.get_group(code)
                    
                    if code not in yearly_agg_groups.groups: continue
                    stock_yearly_stats = yearly_agg_groups.get_group(code)
                    
                    stock_divs = {}
                    if hasattr(div_groups, 'groups') and code in div_groups.groups:
                        div_df = div_groups.get_group(code)
                        for _, row in div_df.iterrows():
                            y = int(row['year'])
                            stock_divs[y] = {
                                'cash': float(row['cash']),
                                'stock': float(row['stock'])
                            }
                    
                    # Apply Patches
                    if str(code) in self.dividend_patches:
                        patches = self.dividend_patches[str(code)]
                        for y_str, data in patches.items():
                            stock_divs[int(y_str)] = data

                    # 7. Run Logic (Highly Optimized with Pre-computed Stats)
                    try:
                        metrics = self.calculator.calculate_complex_simulation(
                            df_group, 
                            start_year, 
                            principal=principal,
                            annual_investment=contribution,
                            dividend_data=stock_divs, 
                            stock_code=code,
                            buy_logic='YEAR_START_OPEN',
                            precomputed_yearly_stats=stock_yearly_stats
                        )
                        
                        if not metrics:
                            continue
                            
                        metrics['stock_code'] = str(code)
                        metrics['stock_name'] = str(code) 
                        metrics['price'] = float(df_group.iloc[-1]['close']) if not df_group.empty else 0.0
                        
                        if len(df_group) > 1:
                            # Vectorized volatility (much faster)
                            close_prices = df_group['close'].values
                            pct_change = np.diff(close_prices) / close_prices[:-1]
                            metrics['volatility_pct'] = float(np.std(pct_change) * 100)
                        else:
                            metrics['volatility_pct'] = 0.0

                        last_valid_y = df_group.iloc[-1]['year']
                        metrics['cagr_pct'] = float(metrics.get(f"s{start_year}e{last_valid_y}bao", 0.0))
                        
                        # CAGR StdDev Calculation
                        traj_values = []
                        for y in years:
                            val = metrics.get(f"s{start_year}e{y}bao")
                            if val is not None:
                                try:
                                    traj_values.append(float(val))
                                except Exception:
                                    pass
                        
                        if len(traj_values) > 1:
                            metrics['cagr_std'] = float(np.std(traj_values))
                        else:
                            metrics['cagr_std'] = 999.0

                        metrics['valid_lasting_years'] = int(len(stock_yearly_stats))  # Number of distinct years
                        metrics['end_year'] = int(last_valid_y)
                        
                        # Globally cast all nested NumPy scalars to native Python primitives for FastAPI JSON
                        metrics = sanitize_numpy(metrics)
                                
                        results.append(metrics)
                            
                    except Exception:
                        # Silently catch per-stock errors to avoid crashing full run
                        continue
                        
                    processed_count += 1
                    
                if processed_count > 0 and (processed_count % 500 == 0 or processed_count == total_stocks):
                    logger.info(f"  Processed {processed_count}/{total_stocks} stocks...")
                
                # CRITICAL: Yield to the event loop after processing each chunk
                # to prevent blocking incoming API requests (e.g. /auth/login)
                import asyncio
                await asyncio.sleep(0)
                    
        finally:
            conn.close()

        # 8. Apply Filters
        filtered_results = self.apply_filters(results)

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Mars Analysis complete. Raw: {len(results)} -> Filtered: {len(filtered_results)} in {duration:.2f}s")
        return filtered_results

    def apply_filters(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply strict filters to ensure quality of results.
        1. Active: End Year == Current Year
        2. Duration: > 3 Years
        3. Volatility: < 3x TSMC Volatility
        4. Stability: CAGR Std < 20
        5. ETF: No 'L' suffix (Leveraged)
        """
        if not results:
            return []
            
        current_year = datetime.now().year
        
        # Find TSMC (2330) Baseline
        tsmc = next((r for r in results if r['stock_code'] == '2330'), None)
        tsmc_vol = tsmc['volatility_pct'] if tsmc else None
        
        filtered = []
        rejected_counts = {'active': 0, 'duration': 0, 'volatility': 0, 'stability': 0, 'etf': 0}
        
        for r in results:
            code = str(r['stock_code'])
            
            # 1. Active Check (Must have data in current year)
            if r.get('end_year', 0) < current_year:
                rejected_counts['active'] += 1
                continue
            
            # 5. ETF Check
            if code.endswith('L'):
                rejected_counts['etf'] += 1
                continue

            # 2. Duration Check (> 3 Years)
            if r.get('valid_lasting_years', 0) <= 3:
                rejected_counts['duration'] += 1
                continue
                
            # 4. Stability Check (Std < 20)
            if r.get('cagr_std', 999) > 20:
                rejected_counts['stability'] += 1
                continue

            # 3. Volatility Check (< 3x TSMC)
            if tsmc_vol and r.get('volatility_pct', 0) > (3 * tsmc_vol):
                rejected_counts['volatility'] += 1
                continue
            
            # Passed all checks (Active check pending implementation of end_year)
            filtered.append(r)
            
        logger.info(f"Filter Stats: {rejected_counts}")
        return filtered

    def export_to_excel(self, data: List[Dict]) -> bytes:
        import pandas as pd
        """
        Export filtered data to Excel binary.
        """
        if not data:
            return b""
            
        df = pd.DataFrame(data)
        
        # Rename & Clean
        df = df.rename(columns={'stock_code': 'id', 'stock_name': 'name'})
        
        valid_yrs = df['valid_lasting_years'] if 'valid_lasting_years' in df.columns else 0
        df['id_name_yrs'] = df['id'].astype(str) + '-' + df['name'].astype(str) + '-' + valid_yrs.astype(str)
        df['valid_years'] = valid_yrs
        
        # Columns
        base_cols = ['id', 'name', 'id_name_yrs', 'valid_years', 'price', 'cagr_pct', 'cagr_std', 'volatility_pct']
        bao_cols = sorted([c for c in df.columns if str(c).startswith('s') and 'bao' in str(c)])
        
        final_cols = [c for c in base_cols + bao_cols if c in df.columns]
        df = df[final_cols]
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()


class CBStrategy:
    """
    Convertible Bond Strategy.
    """
    def __init__(self):
        self.crawler = CBCrawler()
        self.issuance_data = []

    async def initialize(self):
        if not self.issuance_data:
            self.issuance_data = await self.crawler.fetch_issuance_data()

    async def analyze(self, stock_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze CBs for given stocks.
        """
        await self.initialize()
        results = []
        
        for stock_code in stock_ids:
            # 1. Generate Candidates
            candidates = [f"{stock_code}{i}" for i in range(1, 6)]
            
            # 2. Get Stock Price (FAST: DuckDB Latest Price Cache)
            stock_price = MarketDataProvider.get_latest_price(stock_code) or 0.0
            
            for cb_code in candidates:
                # 3. Fetch CB Price
                cb_p, st_p, success = await self.crawler.get_market_data(cb_code, stock_code)
                
                if not success:
                    continue
                    
                # Prefer MarketCache Stock Price if YF failed but we have data
                if st_p == 0 and stock_price > 0:
                    st_p = stock_price
                    
                if cb_p == 0 or st_p == 0:
                    continue

                # 4. Conversion Logic
                conv_price = 0.0
                cb_name = f"{cb_code}"
                
                for record in self.issuance_data:
                    # Match Issuer
                    if record.get('IssuerCode') == stock_code or str(record.get('IssuerCode', '')).endswith(stock_code):
                        try:
                            # Optimistic: If issuance has ConvPrice, use it.
                            cp_val = float(record.get('Conversion/ExchangePriceAtIssuance', 0))
                            if cp_val > 0:
                                conv_price = cp_val
                                cb_name = record.get('ShortName', cb_name)
                                break
                        except Exception:
                            pass
                
                if conv_price == 0:
                    continue

                # 5. Metrics
                parity = (st_p / conv_price) * 100
                premium = ((cb_p - parity) / parity) * 100
                
                results.append({
                    'code': cb_code,
                    'name': cb_name,
                    'cb_price': cb_p,
                    'stock_price': st_p,
                    'conv_price': conv_price,
                    'parity': round(parity, 2),
                    'premium': round(premium, 2),
                    'action': 'HOLD' if premium > 5 else ('BUY' if premium < 0 else 'ACCUMULATE')
                })
                
        return results
