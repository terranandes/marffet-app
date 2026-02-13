

# import pandas as pd # Lazy Import
# import numpy as np # Lazy Import
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from io import BytesIO
import asyncio
from datetime import datetime

# Import existing Services/Crawlers
from app.services.market_data_provider import MarketDataProvider
from app.services.roi_calculator import ROICalculator
from app.project_tw.crawler_cb import CBCrawler

# Setup Logging
logger = logging.getLogger(__name__)

class MarsStrategy:
    def __init__(self):
        self.calculator = ROICalculator()
        self.data_dir = Path("data/raw")
        self.top_50 = []
        # Dividends are now fetched from MarketDataProvider (DuckDB)

    async def analyze(self, stock_ids: List[str], start_year: int = 2006) -> List[Dict[str, Any]]:
        import pandas as pd
        # import numpy as np
        """
        Analyze stocks using MarketDataProvider and ROICalculator.
        """
        # 1. Auto-Detect Universe if needed
        if not stock_ids or stock_ids == ["ALL"]:
            stock_ids = MarketDataProvider.get_stock_list()
            if stock_ids:
                logger.info(f"Auto-detected {len(stock_ids)} stocks from DuckDB.")
            else:
                logger.warning("DuckDB is empty. Cannot auto-detect stocks.")
                return []

        results = []
        end_year = 2025 # Default or current year
        years = list(range(start_year, end_year + 1))
        
        # 2. Dividend Data fetching (now from DuckDB)
        logger.info(f"Using DuckDB for market data and dividends...")
        
        # Load patches once before loop
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

        logger.info(f"Processing {len(stock_ids)} stocks...")
        
        for code in stock_ids:
            try:
                # 3. Fetch History from MarketDataProvider (DuckDB)
                # Mars Strategy needs daily data for high-resolution volatility.
                history_raw = MarketDataProvider.get_daily_history(code, start_date=f"{start_year}-01-01")
                if not history_raw:
                    continue
                
                # Transform to format expected by ROICalculator
                history_list = []
                for h in history_raw:
                    try:
                        dt = datetime.strptime(h['d'], "%Y-%m-%d")
                        history_list.append({
                            'date': dt,
                            'year': dt.year,
                            'month': dt.month,
                            'open': h['o'],
                            'high': h['h'],
                            'low': h['l'],
                            'close': h['c'],
                            'volume': h['v']
                        })
                    except: pass

                if not history_list:
                    continue
                    
                df = pd.DataFrame(history_list)
                
                # 4. Prepare Dividends (DuckDB + Patches)
                stock_divs = {}
                
                # A. Real Data from DuckDB
                db_divs = MarketDataProvider.get_dividends(code, start_year)
                for d in db_divs:
                    y = d['year']
                    stock_divs[y] = {
                        'cash': float(d.get('cash', 0)),
                        'stock': float(d.get('stock', 0))
                    }
                
                # B. PATCHES (Override)

                if code in self.dividend_patches:
                    patches = self.dividend_patches[code]
                    for y_str, data in patches.items():
                        y_int = int(y_str)
                        if y_int in years: # Only apply if year is in range
                            # Merge or Overwrite?
                            # Logic was: if not in stock_divs... etc.
                            # But 2330 case was unconditional overwrite.
                            # 0050 case was "if not in stock_divs".
                            # To be safe and cleaner: We prioritize Patch > Crawler?
                            # 2330: Overwrite. 0050: Supplement.
                            
                            # Let's standardize: Patches ALWAYS Overwrite/Supplement
                            # If we want "Supplement", we check existence.
                            # But distinguishing per stock is messy.
                            # Let's just Overwrite. It's a "Patch" after all.
                            stock_divs[y_int] = data
                
                # 5. Run Logic
                metrics = self.calculator.calculate_complex_simulation(
                    df, 
                    start_year, 
                    dividend_data=stock_divs, 
                    stock_code=code,
                    buy_logic='FIRST_OPEN'
                )
                
                if metrics:
                    metrics['stock_code'] = code
                    metrics['stock_name'] = str(code) 
                    metrics['price'] = df.iloc[-1]['close'] if not df.empty else 0
                    
                    if len(df) > 1:
                        annual_returns = df['close'].pct_change().dropna()
                        metrics['volatility_pct'] = annual_returns.std() * 100
                    else:
                        metrics['volatility_pct'] = 0.0

                    # Fetch CAGR for specific interval
                    last_valid_y = df.iloc[-1]['year']
                    metrics['cagr_pct'] = metrics.get(f"s{start_year}e{last_valid_y}bao", 0)
                    
                    # CAGR StdDev
                    traj_values = []
                    for y in years:
                        val = metrics.get(f"s{start_year}e{y}bao")
                        if val is not None:
                            try:
                                traj_values.append(float(val))
                            except: pass
                    
                    if len(traj_values) > 1:
                        metrics['cagr_std'] = pd.Series(traj_values).std()
                    else:
                        metrics['cagr_std'] = 999.0

                    metrics['valid_lasting_years'] = len(df)
                    results.append(metrics)
                    
            except Exception as e:
                # logger.error(f"Error processing {code}: {e}")
                pass
                
        return results

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
                        except: pass
                
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
