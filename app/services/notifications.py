import yfinance as yf
import pandas as pd
import asyncio
from typing import List, Dict, Any

class NotificationEngine:
    def __init__(self):
        pass

    async def fetch_history(self, ticker: str, period="2y") -> pd.DataFrame:
        """Fetch historical data for SMA calculation"""
        try:
            # Handle TWSE/TPEx suffixes if needed (simple logic for now)
            # Assuming inputs already have .TW or .TWO or can be inferred
            if not (ticker.endswith('.TW') or ticker.endswith('.TWO')):
                # Try inferring based on length
                if len(ticker) == 4:
                    ticker += '.TW' # Most Stocks/ETFs
                elif len(ticker) >= 5:
                    ticker += '.TWO' # CBs commonly on TPEx
                else:
                    ticker += '.TW' # Fallback 
            
            stock = yf.Ticker(ticker)
            hist = await asyncio.to_thread(stock.history, period=period)
            return hist
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return pd.DataFrame()

    async def check_sma_divergence(self, targets: List[Dict]) -> List[Dict]:
        """
        Strategy A: SMA Pair Rebalancing
        Identify Overvalued (> +20% vs SMA) and Undervalued (< -20% vs SMA).
        Suggest pairing them up for exchange.
        """
        alerts = []
        high_candidates = []
        low_candidates = []
        
        for target in targets:
            symbol = target['id']
            hist = await self.fetch_history(symbol)
            if hist.empty or len(hist) < 250:
                continue
            
            hist['SMA_250'] = hist['Close'].rolling(window=250).mean()
            current_price = hist['Close'].iloc[-1]
            sma_250 = hist['SMA_250'].iloc[-1]
            
            if pd.isna(sma_250):
                continue

            divergence = (current_price - sma_250) / sma_250
            
            # Store price for calculation
            info = {'symbol': symbol, 'name': target['name'], 'diff': divergence, 
                    'price': current_price, 'shares': target.get('shares', 0)}
            
            if divergence > 0.20:
                high_candidates.append(info)
            elif divergence < -0.20:
                low_candidates.append(info)

        # Pair up Highs and Lows
        max_pairs = min(len(high_candidates), len(low_candidates))
        for i in range(max_pairs):
            sell = high_candidates[i]
            buy = low_candidates[i]
            
            # 30% Exchange Calculation
            shares_to_sell = int(sell['shares'] * 0.3)
            # Avoid selling 0 shares
            if shares_to_sell < 1: shares_to_sell = 1
            
            sell_value = shares_to_sell * sell['price']
            shares_to_buy = int(sell_value / buy['price'])
            
            msg = (f"⚡ Pair Rebalance: Sell {shares_to_sell} units of {sell['name']} (+{int(sell['diff']*100)}% High) "
                   f"and Buy {shares_to_buy} units of {buy['name']} ({int(buy['diff']*100)}% Low) to balance risk.")
            alerts.append({
                "type": "strategy_sma_pair",
                "level": "warning",
                "message": msg,
                "target_id": f"{sell['symbol']}-{buy['symbol']}"
            })
            
        return alerts

    async def check_market_cap_rebalance(self, targets: List[Dict]) -> List[Dict]:
        """
        Strategy B: Market Cap Pair Rebalancing
        """
        alerts = []
        caps = {}
        prices = {}
        
        # 1. Fetch Caps and Prices
        for target in targets:
            symbol = target['id']
            # ... (suffix logic same as above, can refactor) ...
            if not (symbol.endswith('.TW') or symbol.endswith('.TWO')):
                symbol += '.TW'
                
            try:
                # Optimized: Fetch history once for price? Or use Yahoo info?
                # info endpoint is slow. Let's assume price is fetched elsewhere?
                # For now using yf.Ticker
                ticker = yf.Ticker(symbol)
                # info = await asyncio.to_thread(lambda: ticker.info) # Slow
                # fast_info is better
                fast_info = ticker.fast_info
                mcap = fast_info.market_cap
                price = fast_info.last_price
                
                if mcap:
                    caps[target['id']] = {'cap': mcap, 'price': price, 'shares': target.get('shares', 0), 'name': target['name']}
            except:
                continue
                
        if not caps:
            return []

        # 2. Avg
        avg_cap = sum(c['cap'] for c in caps.values()) / len(caps)
        high_threshold = avg_cap * 1.20
        low_threshold = avg_cap * 0.80
        
        high_caps = []
        low_caps = []
        
        for tid, data in caps.items():
            if data['cap'] > high_threshold:
                high_caps.append({**data, 'symbol': tid})
            elif data['cap'] < low_threshold:
                low_caps.append({**data, 'symbol': tid})

        # Pair
        max_pairs = min(len(high_caps), len(low_caps))
        for i in range(max_pairs):
            sell = high_caps[i]
            buy = low_caps[i]
            
            # 30% Exchange
            shares_to_sell = int(sell['shares'] * 0.3)
            if shares_to_sell < 1: shares_to_sell = 1
            
            sell_value = shares_to_sell * sell['price']
            shares_to_buy = int(sell_value / buy['price'])
            
            msg = (f"⚡ Cap Rebalance: Sell {shares_to_sell} {sell['name']} (High Cap) "
                   f"-> Buy {shares_to_buy} {buy['name']} (Low Cap).")
            alerts.append({
                "type": "strategy_cap_pair",
                "level": "info",
                "message": msg,
                "target_id": f"{sell['symbol']}-{buy['symbol']}"
            })
                
        return alerts


    async def check_cb_alerts(self, targets: List[Dict]) -> List[Dict]:
        """
        Strategy C: Convertible Bond Alerts
        Triggers:
        1. Arbitrage: Premium < -1%
        2. Strong Sell: Premium >= 30%
        """
        alerts = []
        cb_codes = []
        
        # 1. Identify CBs (Suffix 1-9 or 5 digits)
        for t in targets:
            code = t['id']
            # Simple heuristic: CBs often 5 digits (65331) or end with digit
            if len(code) == 5 and code.isdigit():
                 cb_codes.append(code)
        
        if not cb_codes:
            return []
            
        try:
            # Import Strategy (Lazy import to avoid circular dependency if any)
            from project_tw.strategies.cb import CBStrategy
            strategy = CBStrategy()
            results = await strategy.analyze_specific_cbs(cb_codes)
            
            for res in results:
                premium = res.get('premium')
                if isinstance(premium, (int, float)):
                    # Case 1: Arbitrage (< -1%)
                    if premium < -1:
                        msg = f"⚡ CB Arbitrage: {res['name']} ({res['code']}) Premium is {premium}%! {res['description']}"
                        alerts.append({
                            "type": "strategy_cb_arb",
                            "level": "critical", # High Priority
                            "message": msg,
                            "target_id": res['code']
                        })
                    
                    # Case 2: Strong Sell (>= 30%)
                    elif premium >= 30:
                        msg = f"⚡ CB Sell Alert: {res['name']} ({res['code']}) Premium is {premium}%! {res['description']}"
                        alerts.append({
                            "type": "strategy_cb_sell",
                            "level": "warning",
                            "message": msg,
                            "target_id": res['code']
                        })
        except Exception as e:
            print(f"CB Check Error: {e}")
            
        return alerts

    async def generate_alerts(self, portfolio: Dict) -> List[Dict]:
        """
        Main entry point.
        Expects portfolio struct: {'targets': [{'id': '2330', 'name': 'TSMC', ...}], ...}
        """
        all_alerts = []
        targets = portfolio.get('targets', [])
        
        if not targets:
            return []

        # Run checks in parallel
        sma_alerts, cap_alerts, cb_alerts = await asyncio.gather(
            self.check_sma_divergence(targets),
            self.check_market_cap_rebalance(targets),
            self.check_cb_alerts(targets)
        )
        
        all_alerts.extend(sma_alerts)
        all_alerts.extend(cap_alerts)
        all_alerts.extend(cb_alerts)
        
        return all_alerts
