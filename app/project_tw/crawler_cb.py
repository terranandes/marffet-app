
import httpx
import asyncio
import json
import os
# import yfinance as yf # Lazy Import
from datetime import datetime

class CBCrawler:
    def __init__(self, data_dir="data/raw"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.issuance_url = "https://www.tpex.org.tw/openapi/v1/bond_ISSBD5_data"

    async def fetch_issuance_data(self):
        """
        Fetch Static Issuance Data (ISSBD5) from TPEx OpenAPI.
        Returns list of dicts. Cache daily.
        """
        date_str = datetime.now().strftime("%Y%m%d")
        cache_file = os.path.join(self.data_dir, f"CB_Issuance_{date_str}.json")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        try:
            async with httpx.AsyncClient(verify=False) as client:
                # No headers needed for OpenAPI usually, but adding User-Agent is good practice
                headers = {"User-Agent": "MarffetBot/1.0"}
                resp = await client.get(self.issuance_url, headers=headers, timeout=15.0)
                if resp.status_code == 200:
                    data = resp.json()
                    # Cache
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False)
                    return data
                else:
                    print(f"Error fetching CB Issuance: Status {resp.status_code}")
                    return []
        except Exception as e:
            print(f"Error fetching CB Issuance: {e}")
            return []

    async def get_market_data(self, cb_code: str, stock_code: str):
        import yfinance as yf
        """
        Fetch latest market data for CB and Stock using YFinance.
        Returns tuple (cb_close, stock_close, success)
        """
        try:
            # Suffix candidates
            suffixes = ['.TWO', '.TW']
            
            # Construct all combinations to request in one batch? 
            # Or simplified: Request 4 tickers, pick valid ones.
            # YF download is cheap.
            
            tickers_to_try = []
            for s in suffixes:
                tickers_to_try.append(f"{cb_code}{s}")
                tickers_to_try.append(f"{stock_code}{s}")
            
            # Remove duplicates
            tickers_to_try = list(set(tickers_to_try))
            
            # Download
            data = await asyncio.to_thread(yf.download, tickers_to_try, period="5d", progress=False, group_by='ticker', auto_adjust=False)
            
            cb_price = 0.0
            st_price = 0.0
            
            # Helper to find valid price in a dataframe for a list of candidates
            def get_price(candidates, df):
                for t in candidates:
                    if t in df.columns.levels[0]:
                        try:
                            # Get last valid index
                            series = df[t]['Close'].dropna()
                            if not series.empty:
                                return float(series.iloc[-1])
                        except Exception:
                            pass
                return 0.0

            cb_price = get_price([f"{cb_code}.TWO", f"{cb_code}.TW"], data)
            st_price = get_price([f"{stock_code}.TW", f"{stock_code}.TWO"], data)

            if cb_price > 0 and st_price > 0:
                return cb_price, st_price, True
            else:
                 # print(f"Missing data for {cb_code}/{stock_code}. CB: {cb_price}, Stock: {st_price}")
                 return cb_price, st_price, False
            
        except Exception as e:
            print(f"Error fetching market data for {cb_code}: {e}")
            return 0.0, 0.0, False

    def find_cb_for_stock(self, stock_code: str, issuance_data: list):
        """
        Find potential CB codes for a stock from Issuance Data.
        Logic: Match IssuerCode if possible, or try simplistic mapping.
        Note: ISSBD5 'IssuerCode' might differ from 'StockCode'. 
        E.g. Andes 6533, IssuerCode might be 6533?
        """
        for row in issuance_data:
            # Check Issuer Code
            ic = row.get('IssuerCode', '')
            # Strip leading zeros if present? e.g. 00045988
            # If stock code is 6533.
            # Usually IssuerCode == StockCode for public companies.
            
            # Heuristic: Check if StockCode is in IssuerCode or ShortName
            name = row.get('ShortName', '')
            
            if stock_code in ic or stock_code in name:
                # Determine CB Code. ISSBD5 'BondCode' was empty?
                # Rely on naming convention?
                # If ShortName is "Andes CB 1", code is likely 65331.
                # If data lacks BondCode, this is hard.
                # Assuming User provides explicit CB Code is safer.
                pass
        
        # Fallback: Generate candidates
        # 6533 -> 65331, 65332, ...
        return [f"{stock_code}{i}" for i in range(1, 4)]
