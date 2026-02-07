"""
Backend Engines for Martian Investment System
Contains the "Ruthless Manager" logic for Premium Rebalancing Notifications.
"""

from app.database import get_db
from app.services import portfolio_service, market_data_service
from app.repositories import user_repo

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
        targets_by_type = portfolio_service.get_all_targets_by_type(user_id)
        
        # Flatten stocks/ETFs/CBs for price fetching
        all_targets = targets_by_type.get('stock', []) + targets_by_type.get('etf', []) + targets_by_type.get('cb', [])
        if not all_targets:
            return

        stock_ids = [t['stock_id'] for t in all_targets]
        
        # 2. Fetch Live Prices (Batch)
        # Using market_data_service's fetcher which uses yfinance
        live_prices = market_data_service.fetch_live_prices(stock_ids)
        
        # 3. Calculate Portfolio stats (Size Authority)
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
        with get_db() as conn:
            for t in valid_targets:
                sid = t['stock_id']
                name = t['stock_name'] or sid
                price = t['_current_price']
                cap = t['_market_cap']
                asset_type = t.get('asset_type', 'stock')
                
                # --- Trigger 1: Gravity Alert (Mean Reversion) ---
                # Check logic inside check_gravity_alert (which calls repo)
                RuthlessManager.check_gravity_alert(conn, user_id, t, t['_current_price'])
    
                # --- Trigger 2: Size Authority ---
                # Rule: Cap > 1.2 * Avg or < 0.8 * Avg
                if cap > 1.2 * avg_market_cap:
                    user_repo.create_notification(
                        conn,
                        user_id, 'SIZE', 
                        f"Size Authority: {name} Overweight",
                        f"{name} is > 20% larger than your average position size. Trim to balance risk.",
                        target_id=t['id']
                    )
                elif cap < 0.8 * avg_market_cap:
                    user_repo.create_notification(
                        conn,
                        user_id, 'SIZE',
                        f"Size Authority: {name} Underweight",
                        f"{name} is > 20% smaller than your average position size. Accumulate to balance risk.",
                        target_id=t['id']
                    )
    
                # --- Trigger 3: Yield Hunter (CB Arbitrage) ---
                if asset_type == 'cb':
                    # ... (Skipped logic)
                    pass 
    
    @staticmethod
    def check_gravity_alert(conn, user_id, target, current_price):
        """Separate method to handle the specific YF call for SMA."""
        # Clean Code: Use MarketDataService
        try:
        try:
            sid = target['stock_id']
            # Suffix handled by service
            info = market_data_service.fetch_stock_info(sid)
            
            # Use 200DayAverage as proxy for 250Day (industry standard widely avail)
            sma = info.get('twoHundredDayAverage')
            
            if sma:
                if current_price > 1.2 * sma:
                    user_repo.create_notification(
                        conn,
                        user_id, 'GRAVITY',
                        f"Gravity Alert: {target['stock_name']} Euphoria",
                        f"Price ({current_price}) is > 20% above SMA250 ({round(sma, 2)}). Sell the euphoria.",
                        target_id=target['id']
                    )
                elif current_price < 0.8 * sma:
                    user_repo.create_notification(
                        conn,
                        user_id, 'GRAVITY',
                        f"Gravity Alert: {target['stock_name']} Fear",
                        f"Price ({current_price}) is > 20% below SMA250 ({round(sma, 2)}). Buy the fear.",
                        target_id=target['id']
                    )
        except Exception as e:
            print(f"Gravity check failed for {target['stock_id']}: {e}")

