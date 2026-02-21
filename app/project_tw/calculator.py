
# import pandas as pd # Lazy Import
# import numpy as np # Lazy Import

# Split Detector for handling stock splits
try:
    from app.services.split_detector import get_split_detector
    _SPLIT_DETECTOR = None
    
    def _get_detector():
        global _SPLIT_DETECTOR
        if _SPLIT_DETECTOR is None:
            _SPLIT_DETECTOR = get_split_detector()
        return _SPLIT_DETECTOR
except ImportError:
    def _get_detector():
        return None

EXOTIC_PARS = {
    '2327': 2.5,  # 國巨*
    '3093': 5.0,
    '4157': 5.0,
    '4763': 1.0,  # 材料*-KY
    '5266': 5.0,
    '5284': 5.0,
    '5314': 5.0,
    '5488': 5.0,
    '6446': 5.0,
    '6514': 5.0,
    '6524': 5.0,
    '6531': 5.0,  # 愛普*
    '6548': 5.0,
    '6550': 5.0,
    '6576': 5.0,
    '6680': 5.0,
    '6690': 5.0,
    '6708': 5.0,
    '6741': 5.0,
    '6862': 5.0,
    '6919': 0.5,  # 康霈*
    '8424': 5.0,
    '7780': 5.0,
}

class ROICalculator:
    def __init__(self):
        pass

    def calculate_metrics(self, df):
        import numpy as np
        """
        Calculate key metrics for Mars Strategy:
        1. Annualized Return (CAGR)
        2. Volatility (Annualized StdDev of daily returns)
        """
        if df.empty:
            return None

        # Daily Returns using 'close' price
        df['daily_return'] = df['close'].pct_change()
        
        # 1. Total Return
        start_price = df['close'].iloc[0]
        end_price = df['close'].iloc[-1]
        
        if start_price == 0:
            return None

        total_return = (end_price - start_price) / start_price
        
        # Years for CAGR
        days = (df.index[-1] - df.index[0]).days
        years = days / 365.25
        if years < 1:
            years = 1 # Avoid division by small number issues for short periods
            
        cagr = (end_price / start_price) ** (1 / years) - 1
        
        # 2. Volatility (Standard Deviation)
        # Annualized Volatility = StdDev(Daily Returns) * Sqrt(252 trading days)
        daily_std = df['daily_return'].std()
        annual_volatility = daily_std * np.sqrt(252)
        
        return {
            "start_date": df.index[0],
            "end_date": df.index[-1],
            "start_price": start_price,
            "end_price": end_price,
            "total_return_pct": total_return * 100,
            "cagr_pct": cagr * 100,
            "volatility_pct": annual_volatility * 100,
            "data_points": len(df)
        }

    def simulate_dca(self, df, monthly_investment: float):
        """
        Simulate Dollar Cost Averaging.
        Buy 'monthly_investment' amount on the first trading day of each month.
        """
        # Resample to month start (or first available day) -- logic is complex in pure pandas
        # Simplified: Iterate through months
        
        total_invested = 0
        total_shares = 0
        
        # Group by Year-Month
        groups = df.groupby(df.index.to_period('M'))
        
        portfolio_history = []
        
        for period, group in groups:
            # Buy on first day of the month
            day_data = group.iloc[0]
            price = day_data['close']
            
            if price > 0:
                shares_bought = monthly_investment / price
                total_shares += shares_bought
                total_invested += monthly_investment
            
            current_value = total_shares * group.iloc[-1]['close']
            portfolio_history.append({
                "date": str(period),
                "invested": total_invested,
                "value": current_value
            })
            
        final_value = total_shares * df.iloc[-1]['close']
        roi = ((final_value - total_invested) / total_invested) * 100 if total_invested > 0 else 0
        
        return {
            "total_invested": total_invested,
            "final_value": final_value,
            "roi_pct": roi,
            "history": portfolio_history
        }

    def calculate_complex_simulation(self, df, start_year: int, principal: float = 1_000_000, 
                                     annual_investment: float = 60_000, dividend_data: dict = None, stock_code: str = "",
                                     buy_logic: str = 'FIRST_CLOSE'):
        import pandas as pd
        """
        Simulate Mars Strategy: 
        1. Principal 1M (Buy at Year 1).
        2. Yearly Extra 60k (Buy at Year X).
        3. Dividends:
           - Cash: Reinvest at Annual Avg Price.
           - Stock: Add to shares (Par $10 base).
        
        Args:
            buy_logic (str): 'FIRST_CLOSE' | 'YEAR_HIGH' | 'YEAR_LOW' | 'FIRST_OPEN'
        """
        if df.empty:
            return {}

        # Safe Year Extraction
        if 'year' not in df.columns:
            if isinstance(df.index, pd.DatetimeIndex):
                df['year'] = df.index.year
            else:
                # If no year column and no DatetimeIndex, we can't process
                print("ROICalculator Error: DataFrame missing 'year' column and index is not Datetime")
                return {}
                
        years = df['year'].unique()
        yearly_avg_prices = df.groupby('year')['close'].mean()
        
        # Calculate Yearly Action Price based on Logic
        if buy_logic == 'YEAR_HIGH':
            yearly_action_prices = df.groupby('year')['high'].max() # Use HIGH column
            # Fallback if 'high' is missing or 0 
            if yearly_action_prices.max() == 0:
                 yearly_action_prices = df.groupby('year')['close'].max()
        elif buy_logic == 'YEAR_LOW':
            yearly_action_prices = df.groupby('year')['low'].min() # Use LOW column
            if yearly_action_prices.min() == 0:
                 yearly_action_prices = df.groupby('year')['close'].min()
        elif buy_logic == 'FIRST_OPEN':
            yearly_action_prices = df.groupby('year')['open'].first()
        else: # FIRST_CLOSE (Default)
            yearly_action_prices = df.groupby('year')['close'].first()

        yearly_end_prices = df.groupby('year')['close'].last()
        
        sorted_years = sorted([y for y in years if y >= start_year])
        if not sorted_years:
            return {}
            
        current_shares = 0
        total_invested_cash = 0
        
        # Pre-detect splits using full history if available
        # This ensures get_cumulative_ratio has cached data to work with
        detector = _get_detector()
        if detector and stock_code and not df.empty:
            # Convert DF to records for the detector (it expects List[Dict])
            # We only need 'date', 'open', 'close' columns really, but full dict is fine
            detector.detect_splits(stock_code, df.to_dict('records'))
        
        results = {}
        history = []
        
        # Initial Point
        history.append({
            "year": start_year,
            "value": round(principal, 0),
            "dividend": 0,
            "invested": round(principal, 0),
            "roi": 0,
            "cagr": 0
        })
        
        for i, year in enumerate(sorted_years):
            # Price Data
            p_action = yearly_action_prices.get(year, 0) # The price we buy at
            p_end = yearly_end_prices.get(year, 0)
            p_avg = yearly_avg_prices.get(year, 0)
            
            if p_action == 0:
                continue 
            
            # 0. Apply Split FIRST (before buying new shares this year)
            # With nominal prices, a split causes price to drop (e.g., $60 → $15 for 1:4)
            # Existing shares must multiply by the split ratio so value is preserved.
            # New shares bought this year are at the post-split price, so they're already correct.
            # GUARD: Skip if a stock dividend already exists for this year in dividend_data.
            #        Large stock dividends cause ex-rights price drops >40% that the SplitDetector
            #        falsely detects as splits. The dividends table already handles bonus shares
            #        via stock_div_dollar, so applying the split ratio too would double-count.
            detector = _get_detector()
            if detector and stock_code:
                # Year-over-year ratio: only splits that happened THIS year
                prev_year = sorted_years[i - 1] if i > 0 else start_year - 1
                yr_split = detector.get_cumulative_ratio(stock_code, prev_year, year)
                if yr_split != 1.0:
                    # Check for overlapping stock dividend — avoid double-counting
                    has_stock_div = False
                    if dividend_data:
                        div_y = dividend_data.get(year) or dividend_data.get(str(year))
                        if div_y and float(div_y.get('stock', 0)) > 0.5:
                            has_stock_div = True
                    if not has_stock_div:
                        current_shares *= yr_split

            # 1. Dividends FIRST — MoneyCome: 去年留倉部位 (last year's remaining position)
            # Dividends are calculated on shares held BEFORE this year's new investment.
            div_info = {'cash': 0.0, 'stock': 0.0}
            
            if dividend_data:
                # Handle string/int key mismatch
                data_y = dividend_data.get(year) or dividend_data.get(str(year))
                if data_y:
                    div_info.update(data_y)
            
            cash_div_per_share = div_info.get('cash', 0)
            stock_div_dollar = div_info.get('stock', 0)
            
            # Case: Stock Div (on last year's position)
            if stock_div_dollar > 0:
                par_val = EXOTIC_PARS.get(stock_code, 10.0)
                stock_shares_add = current_shares * (stock_div_dollar / par_val)
                current_shares += stock_shares_add
            
            # Case: Cash Div Reinvest (on last year's position, buy at annual avg price)
            total_cash_div = current_shares * cash_div_per_share
            if total_cash_div > 0 and p_avg > 0:
                shares_add = total_cash_div / p_avg
                current_shares += shares_add
            
            # 2. Invest Capital (AFTER dividends — new shares don't get this year's dividend)
            if i == 0:
                # Initial Principal + Extra Input
                amt = principal + annual_investment 
                shares_bought = amt / p_action
                current_shares += shares_bought
                total_invested_cash += amt
            else:
                # Yearly Extra Input
                amt = annual_investment
                shares_bought = amt / p_action
                current_shares += shares_bought
                total_invested_cash += amt

            # 3. Valuation — with nominal prices, no further adjustment needed.
            # current_shares is already in post-split terms.
            total_asset_value = current_shares * p_end
            
            # Use actual investment duration, not global start year
            effective_start_year = sorted_years[0]
            n_yrs = year - effective_start_year + 1
            
            cagr_val = 0.0
            roi_val = 0.0
            
            if total_invested_cash > 0:
                # CAGR
                cagr_raw = (total_asset_value / total_invested_cash) ** (1 / n_yrs) - 1
                cagr_val = round(cagr_raw * 100, 1)
                
                # ROI
                roi_raw = (total_asset_value - total_invested_cash) / total_invested_cash
                roi_val = round(roi_raw * 100, 1)

                results[f"s{start_year}e{year}bao"] = cagr_val
            else:
                results[f"s{start_year}e{year}bao"] = 0.0
                
            # History Tracking
            history.append({
                "year": year,
                "value": round(total_asset_value, 0),
                "dividend": round(total_cash_div, 0),
                "invested": round(total_invested_cash, 0),
                "roi": roi_val,
                "cagr": cagr_val
            })

            # Check for final year to populate Final Value
            if year == sorted_years[-1]:
                results["finalValue"] = round(total_asset_value, 0)
                results["totalCost"] = round(total_invested_cash, 0)

        # Handle Bankrupt / Delisted / Acquired Stocks (Fill timeline to 2026 for Grand Correlation)
        # If the stock ceases to trade (e.g., Kolin 1606 ends in 2008, SPIL 2325 ends in 2018), 
        # MoneyCome calculates terminal CAGR up to the target year (e.g., 2026) using the final salvaged/buyout value.
        # We simulate the remaining years by FREEZING the last known total_asset_value and total_invested_cash.
        target_max_year = 2026
        if sorted_years[-1] < target_max_year:
            # FREEZE AT LAST KNOWN VALUE (Do not force 0.0)
            terminal_value = total_asset_value 
            for year in range(sorted_years[-1] + 1, target_max_year + 1):
                n_yrs = year - sorted_years[0] + 1
                
                # Investment capital remains frozen at the last known amount.
                cagr_raw = (terminal_value / total_invested_cash) ** (1 / n_yrs) - 1 if total_invested_cash > 0 else 0
                cagr_val = round(cagr_raw * 100, 1)
                
                roi_raw = (terminal_value - total_invested_cash) / total_invested_cash if total_invested_cash > 0 else 0
                roi_val = round(roi_raw * 100, 1)
                
                results[f"s{start_year}e{year}bao"] = cagr_val
                
                history.append({
                    "year": year,
                    "value": round(terminal_value, 0),
                    "dividend": 0.0,
                    "invested": round(total_invested_cash, 0),
                    "roi": roi_val,
                    "cagr": cagr_val
                })
                
                if year == target_max_year:
                     results["finalValue"] = round(terminal_value, 0)
                     results["totalCost"] = round(total_invested_cash, 0)

                
        results[f"s{start_year}e{sorted_years[-1]}yrs"] = len(sorted_years)
        results["history"] = history
        return results

    def calculate_yearly_cumulative_cagr(self, df, start_year: int):
        """
        Calculate cumulative CAGR (Compound Annual Growth Rate) from start_year to each year end.
        Output keys: 's{start_year}e{year}bao' (e.g., s2006e2025bao)
        Metric: ((End Price of Year Y / Start Price of Start Year) ^ (1 / Years)) - 1
        """
        if df.empty:
            return {}

        results = {}
        
        # Determine Base Price (Buy At Opening of the first available day)
        base_price = df.iloc[0]['open']
        if base_price == 0:
            base_price = df.iloc[0]['close'] # Fallback
            
        if base_price == 0:
            return {}

        # Iterate through each year present in the data
        years = df.index.year.unique()
        
        for year in years:
            if year <= start_year:
                continue
                
            # Get the last available price for that year
            year_data = df[df.index.year == year]
            if year_data.empty:
                continue
                
            end_price = year_data.iloc[-1]['close']
            
            # Calculate CAGR
            # n = number of years elapsed. e.g. 2006 to 2007 is 1 year.
            n_years = year - start_year
            if n_years <= 0:
                n_years = 1 # Safety
                
            if base_price > 0 and end_price > 0:
                 cagr = (float(end_price) / float(base_price)) ** (1 / float(n_years)) - 1
                 val = cagr * 100 # Convert to percentage
            else:
                 val = 0
            
            col_name = f"s{start_year}e{year}bao"
            results[col_name] = round(val, 1)
            
        # Also add years count column
        duration = len(years)
        results[f"s{start_year}e{years[-1]}yrs"] = duration
            
        return results
