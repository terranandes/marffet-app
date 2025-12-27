import asyncio
from project_tw.crawler_cb import CBCrawler

class CBStrategy:
    """
    Convertible Bond (CB) Strategy
    Based on 'CB6533.xlsx' Logic.
    
    Key Metric: Premium Rate (I2) = (Bond Price - Conversion Value) / Conversion Value? 
    Or user's definition: '溢價率'.
    """
    
    def __init__(self, data_dir="data/raw"):
        # Thresholds from Excel
        self.buy_threshold = 0.0 # < 0% -> Buy
        self.consider_buy_threshold = 3.5 # 0 ~ 3.5% -> Consider Buy
        self.hold_threshold = 7.0 # 3.5 ~ 7% -> Hold
        self.consider_sell_threshold = 15.0 # 7 ~ 15% -> Consider Sell
        self.sell_threshold = 30.0 # 15 ~ 30% -> Sell, > 30% -> Immediate Sell
        
        self.crawler = CBCrawler(data_dir=data_dir)
        self.issuance_data = []

    async def initialize(self):
        """Fetch/Load Static Data"""
        self.issuance_data = await self.crawler.fetch_issuance_data()
        print(f"CB Strategy Initialized. Loaded {len(self.issuance_data)} issuance records.")

    async def analyze_list(self, stock_codes: list):
        """
        Analyze a list of stocks to find associated CBs and evaluate them.
        """
        results = []
        
        # Ensure initialized
        if not self.issuance_data:
            await self.initialize()

        for stock in stock_codes:
            # 1. Find Candidate CBs
            # Heuristic: Try suffix 1, 2, 3 OR match issuance data
            # For now, simplistic scan
            candidates = [f"{stock}{i}" for i in range(1, 4)]
            
            # 2. Filter Candidates that exist in Issuance Data (Optional but good for Metadata)
            # Map code to issuance record
            active_cbs = []
            for cand in candidates:
                # Find in issuance (by partial match in ShortName or brute force?)
                # ISSBD5 doesn't strictly have the 5-digit code in 'BondCode' field reliably.
                # So we relay on YFinance to validate existence.
                active_cbs.append(cand)
                
            for cb_code in active_cbs:
                # 3. Fetch Market Data
                cb_price, st_price, success = await self.crawler.get_market_data(cb_code, stock)
                
                if not success or cb_price == 0 or st_price == 0:
                     continue
                     
                # 4. Determine Conversion Price
                # Try to find in Issuance Data
                conv_price = 0.0
                cb_name = f"{cb_code}_UNKNOWN"
                
                # Search Issuance by IssuerCode?
                # This is tricky without exact mapping.
                # Heuristic: Find record where IssuerCode ~= StockCode AND name matches suffix?
                # Let's try to match by ShortName using `stock` + `numeric suffix`?
                # e.g. "6533" -> "雅德" (Name from where?)?
                
                # Fallback: Estimate Conversion Price? 
                # Premium = (CB - Parity) / Parity. 
                # Parity = (Stock / Conv) * 100.
                # We need Conv Price.
                
                # If we cannot find it, we cannot calculate Premium.
                # For now, default to 100.0 (Par) or Log Warning.
                
                # Try to parse from ISSBD5 if possible.
                # Iterate all issuance
                matched_issuance = None
                for record in self.issuance_data:
                    # check if IssuerCode ends with StockCode
                    # e.g. 00045988 (No), 6533 (Yes).
                    # Actually IssuerCode (public) is usually just the stock code.
                    issuer = record.get('IssuerCode', '').strip()
                    if issuer == stock or issuer.endswith(stock):
                        # Potential Match. Check series?
                        # If SeriesNumber matches end of CB Code?
                        # e.g. CB 65331 -> Series 1?
                        # record['SeriesNumber'] might be '1', '114' etc.
                        # record['TrancheNumber'] might be '1'.
                        
                        # Let's assume if we find *any* issuance for this stock, use its Conv Price
                        # Refine later.
                        matched_issuance = record
                        cb_name = record.get('ShortName', cb_name)
                        try:
                            cp_str = record.get('Conversion/ExchangePriceAtIssuance', '0')
                            conv_price = float(cp_str)
                        except: pass
                        break
                
                if conv_price == 0:
                    # Cannot analyze without Conversion Price (Static)
                    # Use a placeholder result
                    print(f"WARN: Missing Conversion Price for {cb_code}. Skipping Premium Calc.")
                    result = {
                        'code': cb_code,
                        'name': cb_name,
                        'cb_price': cb_price,
                        'stock_price': st_price,
                        'conv_price': 'N/A',
                        'premium': 'N/A',
                        'action': 'UNKNOWN',
                        'confidence': 'LOW'
                    }
                else:
                    # 5. Calculate Metrics
                    parity = (st_price / conv_price) * 100
                    premium = ((cb_price - parity) / parity) * 100 if parity > 0 else 0
                    
                    # 6. Evaluate
                    eval_res = self.evaluate(cb_code, premium)
                    
                    result = {
                        'code': cb_code,
                        'name': cb_name,
                        'cb_price': cb_price,
                        'stock_price': st_price,
                        'conv_price': conv_price,
                        'parity': round(parity, 2),
                        'premium': round(premium, 2),
                        'action': eval_res['action'],
                        'description': eval_res['description'],
                        'confidence': eval_res['confidence']
                    }
                
                results.append(result)
                
        return results

    def evaluate(self, cb_code: str, premium_rate: float, expiry_days: int = 365):
        """
        Evaluate action based on Premium Rate (%).
        """
        result = {
            'code': cb_code,
            'premium_rate': premium_rate,
            'action': 'HOLD',
            'description': '',
            'confidence': 'NEUTRAL'
        }
        
        # Logic Hierarchy
        if premium_rate < self.buy_threshold:
            # < 0%
            result['action'] = 'STRONG_BUY'
            result['description'] = "套利警報：訊號出現！立即精算所有交易成本，確認利潤空間。(或有轉換價值)"
            result['confidence'] = 'HIGH'
            
        elif self.buy_threshold <= premium_rate < self.consider_buy_threshold:
            # 0 ~ 3.5%
            result['action'] = 'BUY'
            result['description'] = "最佳買點：此時買入CB的性價比最高，是建立多頭部位的首選。(到期日前還是得轉換)"
            result['confidence'] = 'MEDIUM'
            
        elif self.consider_buy_threshold <= premium_rate < self.hold_threshold:
            # 3.5 ~ 7%
            result['action'] = 'HOLD'
            result['description'] = "續抱：利潤開始擴大，但尚未達到瘋狂程度。(享受主升段)"
            result['confidence'] = 'HIGH'
            
        elif self.hold_threshold <= premium_rate < self.consider_sell_threshold:
            # 7 ~ 15%
            result['action'] = 'CONSIDER_SELL'
            result['description'] = "考慮賣出：漲幅已大，注意回檔風險。(可開始分批獲利)"
            result['confidence'] = 'MEDIUM'
            
        elif self.consider_sell_threshold <= premium_rate < self.sell_threshold:
            # 15 ~ 30%
            result['action'] = 'SELL'
            result['description'] = "賣出CB，買回現股：機會成本過高，轉持現股參與更有利。(若看好後市)"
            result['confidence'] = 'HIGH'
            
        else:
            # >= 30%
            result['action'] = 'STRONG_SELL'
            result['description'] = "立即賣出：乖離過大，價格極度不合理。(獲利了結，尋找下一個標的)"
            result['confidence'] = 'HIGH'
            
        return result
