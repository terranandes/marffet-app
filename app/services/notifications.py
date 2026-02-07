from app.services import market_data_service
import pandas as pd
import asyncio
from typing import List, Dict, Any

class NotificationEngine:
    def __init__(self):
        pass

    async def fetch_history(self, ticker: str, period="2y") -> pd.DataFrame:
        """Fetch historical data for SMA calculation"""
        def __init__(self):
        pass

    async def fetch_history(self, ticker: str, period="2y") -> pd.DataFrame:
        """Fetch historical data for SMA calculation"""
        # Clean Code: Use MarketDataService
        return await asyncio.to_thread(market_data_service.fetch_history_series, ticker, period)

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
                # Clean Code: Use MarketDataService
                info = await asyncio.to_thread(market_data_service.fetch_stock_info, symbol)
                mcap = info.get('marketCap')
                price = info.get('lastPrice')
                
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
        Strategy C: Convertible Bond Alerts (Premium Tier)
        Triggers:
        1. Arbitrage: Premium < -1% → Buy CB, Sell Stock
        2. Strong Sell: Premium >= 30% → Sell CB, Buy Stock
        
        Includes rebalancing advice with calculated share quantities.
        """
        alerts = []
        cb_targets = {}
        stock_targets = {}
        
        # 1. Separate CBs and Stocks, build lookup maps
        for t in targets:
            code = t['id']
            if len(code) == 5 and code.isdigit():
                cb_targets[code] = t  # CB
            elif len(code) == 4 and code.isdigit():
                stock_targets[code] = t  # Stock
        
        if not cb_targets:
            return []
            
        try:
            from app.project_tw.strategies.cb import CBStrategy
            strategy = CBStrategy()
            results = await strategy.analyze_specific_cbs(list(cb_targets.keys()))
            
            for res in results:
                premium = res.get('premium')
                if not isinstance(premium, (int, float)):
                    continue
                
                cb_code = res['code']
                stock_code = cb_code[:4]  # Infer stock from CB (e.g., 65331 -> 6533)
                
                # Get portfolio holdings
                cb_holding = cb_targets.get(cb_code, {})
                stock_holding = stock_targets.get(stock_code, {})
                
                cb_shares = cb_holding.get('shares', 0)
                stock_shares = stock_holding.get('shares', 0)
                
                cb_price = res.get('cb_price', 0)
                stock_price = res.get('stock_price', 0)
                conv_price = res.get('conv_price', 0)
                
                # === Rebalancing Logic (Target: Equal Weight 50/50) ===
                current_cb_val = cb_shares * (cb_price * 1000) # CB is 1000/share? usually 100 TWD face value, quoted as e.g. 105. 
                # Wait, CB price in Taiwan is usually quoted as e.g. 110.5 (Dollars?). One sheet is 100,000 face value.
                # Usually 1 "Share" in DB means 1 Sheet (100k)? Or 1 unit (100)?
                # Let's assume input 'shares' for CB is number of 'sheets' (張).
                # Live Price 101 means 101 TWD per 100 TWD face value? No, usually quote is 100-base.
                # 1 Sheet = 100,000 TWD face value. Price 105 => Market Value 105,000.
                # Crawler returns price? e.g. 120. 
                # So Value = shares * price * 1000? 
                # Wait, if price is 120, and face is 100. It's 1.2x.
                # If face is 100,000. Value is 120,000.
                # So Multiplier is 1000. (120 * 1000 = 120,000). Yes.

                current_cb_val = cb_shares * cb_price * 1000
                current_stock_val = stock_shares * stock_price
                
                total_val = current_cb_val + current_stock_val
                target_val = total_val / 2
                
                # Deviation
                diff_val = target_val - current_stock_val # If positive, buy stock. If negative, sell stock.
                
                rebalance_msg = ""
                
                # Alert Generation
                msg_header = f"⚡ CB Premium Alert: {res['name']}"
                
                if premium < -1:
                    # Case 1: Arbitrage (CB Cheap).
                    # Suggestion: Buy CB, Sell Stock to reach Equal?
                    # Or just Buy CB? User said "rebalance ... to be fair/equal".
                    # We should move capital FROM Stock TO CB until equal.
                    
                    if current_cb_val < target_val:
                        # CB is underweight (and cheap!). Buy CB.
                        shortfall = target_val - current_cb_val
                        # Sell Stock to fund it? Or just Buy?
                        # "Rebalance" implies shifting.
                        # Sell Stock amount = shortfall.
                        stock_to_sell = int(shortfall / stock_price) if stock_price > 0 else 0
                        cb_to_buy = int(shortfall / (cb_price * 1000)) if cb_price > 0 else 0
                        
                        rebalance_msg = (
                             f"\n⚖️ **Rebalance to Equal**:\n"
                             f"  • Strategy: CB Undervalued (< -1%). Equalize weights.\n"
                             f"  • Action: Sell {stock_to_sell:,} shares of Stock ({stock_code})\n"
                             f"  • Action: Buy {cb_to_buy} units of CB ({cb_code})\n"
                        )
                    else:
                         rebalance_msg = "\n⚖️ **Status**: CB is Cheap but already Overweight. Consider holding."

                    alerts.append({
                        "type": "strategy_cb_arb",
                        "level": "critical",
                        "message": f"{msg_header}\nPremium: {premium:.2f}%\n{rebalance_msg}",
                        "target_id": cb_code
                    })

                elif premium >= 30:
                    # Case 2: Expensive (CB Expensive).
                    # Suggestion: Sell CB, Buy Stock?
                    
                    if current_cb_val > target_val:
                        # CB is Overweight (and expensive!). Sell CB.
                        excess = current_cb_val - target_val
                        cb_to_sell = int(excess / (cb_price * 1000)) if cb_price > 0 else 0
                        stock_to_buy = int(excess / stock_price) if stock_price > 0 else 0
                        
                        rebalance_msg = (
                             f"\n⚖️ **Rebalance to Equal**:\n"
                             f"  • Strategy: CB Overvalued (>= 30%). Equalize weights.\n"
                             f"  • Action: Sell {cb_to_sell} units of CB ({cb_code})\n"
                             f"  • Action: Buy {stock_to_buy:,} shares of Stock ({stock_code})\n"
                        )
                    else:
                        rebalance_msg = "\n⚖️ **Status**: CB is Expensive but Underweight. Consider holding or selling all."

                    alerts.append({
                        "type": "strategy_cb_sell",
                        "level": "warning",
                        "message": f"{msg_header}\nPremium: {premium:.2f}%\n{rebalance_msg}",
                        "target_id": cb_code
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
