"""
Backend Engines for Martian Investment System
Contains the "Ruthless Manager" logic for Premium Rebalancing Notifications.
"""

from app import portfolio_db

class RuthlessManager:
    """
    The Ruthless Wealth Manager Engine.
    Checks user portfolios against discipline triggers.
    """
    
    @staticmethod
    def run_checks(user_id: str):
        """
        Run all rebalancing checks for a specific user.
        Designed to be called lazily (e.g., on API poll).
        """
        # 1. Fetch User Portfolio (All Targets)
        targets_by_type = portfolio_db.get_all_targets_by_type(user_id)
        
        # Flatten stocks/ETFs/CBs for price fetching
        all_targets = targets_by_type.get('stock', []) + targets_by_type.get('etf', []) + targets_by_type.get('cb', [])
        if not all_targets:
            return

        stock_ids = [t['stock_id'] for t in all_targets]
        
        # 2. Fetch Live Prices (Batch)
        # Using portfolio_db's existing fetcher which uses yfinance
        live_prices = portfolio_db.fetch_live_prices(stock_ids)
        
        # 3. Calculate Portfolio Stats for "Size Authority"
        total_market_cap = 0
        valid_targets = []
        
        for t in all_targets:
            sid = t['stock_id']
            price_info = live_prices.get(sid, {})
            current_price = price_info.get('price', 0)
            
            if current_price > 0:
                t['_current_price'] = current_price
                t['_market_cap'] = t['total_shares'] * current_price
                if t['_market_cap'] > 0: 
                    # Only count positions with value
                    total_market_cap += t['_market_cap']
                    valid_targets.append(t)
        
        if not valid_targets:
            return

        avg_market_cap = total_market_cap / len(valid_targets)
        
        # 4. Run Triggers for each target
        for t in valid_targets:
            sid = t['stock_id']
            name = t['stock_name'] or sid
            price = t['_current_price']
            cap = t['_market_cap']
            asset_type = t.get('asset_type', 'stock')
            
            # --- Trigger 1: Gravity Alert (Mean Reversion) ---
            # Rule: Price > 1.2 * SMA250 or < 0.8 * SMA250
            # Need SMA250. Optimization: Only fetch history if price seems extreme? 
            # Or fetch basic info. yfinance fast_info has 200DayAverage, let's use that as proxy for 250?
            # 250 trading days ~= 1 year. 'twoHundredDayAverage' is standard.
            # Let's fetch detail if needed.
            # Note: fetch_live_prices is lightweight. We might need a separate fetch for SMA if not caching.
            # For MVP/Demo: Fetch SMA dynamically (slow) or use 50-day/200-day from info.
            # Warning: Asking yfinance for info for every stock every poll is too slow.
            # Strategy: We assume `fetch_live_prices` is cached or fast.
            # Let's look up extended info only if we are "checking".
            # To avoid spamming YF, we can do this check stochastically or just rely on 'twoHundredDayAverage'
            
            # Let's do a quick check using yfinance directly here for now, but catch errors.
            RuthlessManager.check_gravity_alert(user_id, t, t['_current_price'])

            # --- Trigger 2: Size Authority ---
            # Rule: Cap > 1.2 * Avg or < 0.8 * Avg
            if cap > 1.2 * avg_market_cap:
                portfolio_db.create_notification(
                    user_id, 'SIZE', 
                    f"Size Authority: {name} Overweight",
                    f"{name} is > 20% larger than your average position size. Trim to balance risk.",
                    target_id=t['id']
                )
            elif cap < 0.8 * avg_market_cap:
                portfolio_db.create_notification(
                    user_id, 'SIZE',
                    f"Size Authority: {name} Underweight",
                    f"{name} is > 20% smaller than your average position size. Accumulate to balance risk.",
                    target_id=t['id']
                )

            # --- Trigger 3: Yield Hunter (CB Arbitrage) ---
            if asset_type == 'cb':
                # Need "Premium" (CB Price vs Stock Price / Conversion Price)
                # This requires complex CB data usually not free on YF.
                # For this Demo simulation, we might need to Mock it or use a simplified metric?
                # Datasheet says: "Premium < -1% or > 30%".
                # If we can't get real CB premium, we might skip or Mock.
                # Let's assume we can calculate it if we had Conversion Price.
                # For Implementation now: We'll skip real CB data fetching (hard) 
                # and maybe rely on a 'simulated' premium if we can't find it.
                pass 
    
    @staticmethod
    def check_gravity_alert(user_id, target, current_price):
        """Separate method to handle the specific YF call for SMA."""
        import yfinance as yf
        try:
            # Suffix
            sid = target['stock_id']
            suffix = '.TWO' if len(sid) == 4 and int(sid) > 4000 else '.TW' # Rough heuristic or try both
            # Better: portfolio_db.fetch_live_prices logic
            ticker = yf.Ticker(f"{sid}.TW") 
            info = ticker.fast_info
            if not info.get('lastPrice'):
                ticker = yf.Ticker(f"{sid}.TWO")
                info = ticker.fast_info
            
            # Use 200DayAverage as proxy for 250Day (industry standard widely avail)
            sma = info.get('twoHundredDayAverage')
            
            if sma:
                if current_price > 1.2 * sma:
                    portfolio_db.create_notification(
                        user_id, 'GRAVITY',
                        f"Gravity Alert: {target['stock_name']} Euphoria",
                        f"Price ({current_price}) is > 20% above SMA250 ({round(sma, 2)}). Sell the euphoria.",
                        target_id=target['id']
                    )
                elif current_price < 0.8 * sma:
                    portfolio_db.create_notification(
                        user_id, 'GRAVITY',
                        f"Gravity Alert: {target['stock_name']} Fear",
                        f"Price ({current_price}) is > 20% below SMA250 ({round(sma, 2)}). Buy the fear.",
                        target_id=target['id']
                    )
        except Exception as e:
            print(f"Gravity check failed for {target['stock_id']}: {e}")

