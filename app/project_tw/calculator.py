
import pandas as pd
import numpy as np

class ROICalculator:
    def __init__(self):
        pass

    def calculate_metrics(self, df: pd.DataFrame):
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

    def simulate_dca(self, df: pd.DataFrame, monthly_investment: float):
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

    def calculate_complex_simulation(self, df: pd.DataFrame, start_year: int, principal: float = 1_000_000, 
                                     annual_investment: float = 60_000, dividend_data: dict = None, stock_code: str = "",
                                     buy_logic: str = 'FIRST_CLOSE'):
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
            
            if p_action == 0: continue
            
            # 1. Invest Capital
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
            
            # 2. Dividends
            # Default from passed data or 0
            div_info = {'cash': 0.0, 'stock': 0.0}
            
            if dividend_data:
                # Handle string/int key mismatch
                data_y = dividend_data.get(year) or dividend_data.get(str(year))
                if data_y:
                    div_info.update(data_y)
            
            # Calculate dividends
            cash_div_per_share = div_info.get('cash', 0)
            stock_div_dollar = div_info.get('stock', 0)
            
            # Case: Stock Div
            if stock_div_dollar > 0:
                # Based on Current Shares (Buy at Open qualifies for Mid-Year Div)
                stock_shares_add = current_shares * (stock_div_dollar / 10.0)
                current_shares += stock_shares_add
            
            # Case: Cash Div Reinvest
            # Based on Current Shares
            total_cash_div = current_shares * cash_div_per_share
            if total_cash_div > 0 and p_avg > 0:
                shares_add = total_cash_div / p_avg
                current_shares += shares_add

            # Metric Calculation
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
                
        results[f"s{start_year}e{sorted_years[-1]}yrs"] = len(sorted_years)
        results["history"] = history
        return results

    def calculate_yearly_cumulative_cagr(self, df: pd.DataFrame, start_year: int):
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
