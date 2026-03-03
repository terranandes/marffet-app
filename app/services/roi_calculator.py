

# import pandas as pd # Lazy Import
# import numpy as np # Lazy Import
from typing import Dict, Any, Optional

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

class ROICalculator:
    def __init__(self):
        pass

    def calculate_metrics(self, df: Any) -> Optional[Dict[str, Any]]:
        import numpy as np
        """
        Calculate key metrics for Mars Strategy:
        1. Annualized Return (CAGR)
        2. Volatility (Annualized StdDev of daily returns)
        """
        if df.empty:
            return None

        # Daily Returns using 'close' price
        df = df.copy() # Avoid SettingWithCopyWarning
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

    def simulate_dca(self, df: Any, monthly_investment: float):
        import pandas as pd
        """
        Simulate Dollar Cost Averaging.
        Buy 'monthly_investment' amount on the first trading day of each month.
        """
        if df.empty:
            return {
                "total_invested": 0,
                "final_value": 0,
                "roi_pct": 0,
                "history": []
            }

        # Resample to month start (or first available day) -- logic is complex in pure pandas
        # Simplified: Iterate through months
        
        total_invested = 0
        total_shares = 0
        
        # Group by Year-Month
        # Ensure index is DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
             # Try to convert if it's not
             try:
                 df.index = pd.to_datetime(df.index)
             except Exception:
                 pass

        if isinstance(df.index, pd.DatetimeIndex):
            groups = df.groupby(df.index.to_period('M'))
        else:
             # Fallback if index isn't datetime and can't be converted
             # But usually df should have datetime index
             return {
                "total_invested": 0,
                "final_value": 0,
                "roi_pct": 0,
                "history": []
            }
        
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

    def calculate_complex_simulation(self, df: Any, start_year: int, principal: float = 1_000_000, 
                                     annual_investment: float = 60_000, dividend_data: dict = None, stock_code: str = "",
                                     buy_logic: str = 'YEAR_START_OPEN', precomputed_yearly_stats: Any = None):
        import pandas as pd
        """
        Simulate Mars Strategy: 
        1. Principal 1M (Buy at Year 1).
        2. Yearly Extra 60k (Buy at Year X).
        3. Dividends:
           - Cash: Reinvest at Annual Avg Price.
           - Stock: Add to shares (Par $10 base).
        
        Args:
            buy_logic (str): 'FIRST_CLOSE' | 'YEAR_HIGH' | 'YEAR_LOW' | 'YEAR_START_OPEN'
            precomputed_yearly_stats (DataFrame): Optional pre-aggregated yearly stats (action_price, avg_price, end_price)
        """
        if df.empty and precomputed_yearly_stats is None:
            return {}

        # 1. Price Standard Reconciliation (Reconcile Nominal vs Adjusted)
        # Some stocks in DuckDB are pre-adjusted (e.g. 2542 at 1.7 in 2006)
        # Some are nominal (e.g. 2330 at 58 in 2006).
        detector = _get_detector()
        is_pre_adjusted = False
        if detector and not df.empty and stock_code:
            try:
                first_row = df.iloc[0]
                first_price = first_row['close']
                first_year = int(first_row.name.year) if hasattr(first_row.name, 'year') else start_year
                # If price is extremely low (<20) but we have significant splits later (ratio > 2)
                # it's almost certainly already split-adjusted in the source.
                ratio_2026 = detector.get_cumulative_ratio(str(stock_code), first_year, 2026)
                if ratio_2026 > 2.0 and first_price < 20.0:
                    is_pre_adjusted = True
            except Exception:
                pass
            
        if precomputed_yearly_stats is not None:
            # Use pre-aggregated data (much faster)
            df_yearly = precomputed_yearly_stats
            df_yearly.set_index('year')['avg_price']
            yearly_end_prices = df_yearly.set_index('year')['end_price']
            yearly_action_prices = df_yearly.set_index('year')['action_price']
            sorted_years = sorted([y for y in df_yearly['year'].unique() if y >= start_year])
        else:
            # Fallback to slow per-stock groupby
            df = df.copy()
            if 'year' not in df.columns:
                if isinstance(df.index, pd.DatetimeIndex):
                    df['year'] = df.index.year
                else:
                    return {}
                    
            years = df['year'].unique()
            df.groupby('year')['close'].mean()
            
            if buy_logic == 'YEAR_HIGH':
                yearly_action_prices = df.groupby('year')['high'].max()
            elif buy_logic == 'YEAR_LOW':
                yearly_action_prices = df.groupby('year')['low'].min()
            elif buy_logic == 'FIRST_OPEN' or buy_logic == 'YEAR_START_OPEN':
                yearly_action_prices = df.groupby('year')['open'].first()
            else:
                yearly_action_prices = df.groupby('year')['close'].first()

            yearly_end_prices = df.groupby('year')['close'].last()
            # Filter: keep only the latest contiguous block of years
            # This removes pre-IPO / 興櫃 (emerging board) data that precedes
            # a gap before the stock's main board listing (IPO).
            year_counts = df.groupby('year').size()
            substantial_years = sorted([y for y in years if y >= start_year and year_counts.get(y, 0) >= 20])
            if substantial_years:
                # Split into contiguous groups (gap > 1 year = new group)
                groups = [[substantial_years[0]]]
                for y in substantial_years[1:]:
                    if y - groups[-1][-1] <= 1:
                        groups[-1].append(y)
                    else:
                        groups.append([y])
                # Keep only the latest (most recent) contiguous group
                sorted_years = groups[-1]
            else:
                sorted_years = []
        if not sorted_years:
            return {}
            
        current_shares = 0
        total_invested_cash = 0
        
        # Pre-detect splits using full history if available
        # This ensures get_cumulative_ratio has cached data to work with
        detector = _get_detector()
        if detector and stock_code and not df.empty:
            # PERFORMANCE: Use numpy arrays directly instead of to_dict('records')
            # The detector needs open/close/high prices + year for each row.
            # We build a minimal list only with needed columns using zip (10x faster).
            if stock_code not in detector._cache:
                df.reset_index()
                close_vals = df['close'].values
                open_vals = df['open'].values
                high_vals = df['high'].values if 'high' in df.columns else open_vals
                year_vals = df['year'].values if 'year' in df.columns else [0] * len(df)
                
                # Build minimal records only for split detection
                records = [
                    {'close': float(c), 'open': float(o), 'high': float(h), 'year': int(y)}
                    for c, o, h, y in zip(close_vals, open_vals, high_vals, year_vals)
                ]
                detector.detect_splits(stock_code, records)
        
        results = {}
        history = []
        
        # Initial Point (year before simulation starts — pre-investment baseline)
        history.append({
            "year": start_year - 1,
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
            
            # MoneyCome Methodology: Reinvestment Price = (Start + End) / 2
            p_reinvest = (p_action + p_end) / 2.0
            
            if p_action == 0:
                continue 
            
            # 1. Invest Capital & Calculate Multi-Year Effects
            if i == 0:
                # Initial Principal is bought at Start Price (Opening)
                current_shares = principal / p_action
                total_invested_cash = principal
            
            # --- START DIVIDEND BASE CAPTURE ---
            # Rule: Dividends are calculated based on Carry-over Shares (留倉部位)
            # which means shares held BEFORE the current year's contribution/reinvestment.
            
            # Extract dividends for this year
            div_info = {'cash': 0.0, 'stock': 0.0}
            if dividend_data:
                data_y = dividend_data.get(year) or dividend_data.get(str(year))
                if data_y:
                    div_info.update(data_y)
            
            cash_div_per_share = div_info.get('cash', 0)
            stock_div_dollar = div_info.get('stock', 0)
            
            total_cash_div = current_shares * cash_div_per_share
            # ------------------------------------

            # 2. Add Annual Contribution & Reinvest Dividends at Midpoint
            # Rule: Both contribution and dividends are reinvested at (Start + End) / 2
            
            # Add Contribution
            contrib_shares = annual_investment / p_reinvest
            current_shares += contrib_shares
            total_invested_cash += annual_investment
            
            # Reinvest Cash Dividends
            if total_cash_div > 0 and p_reinvest > 0:
                div_shares = total_cash_div / p_reinvest
                current_shares += div_shares
            
            # 3. Stock Dividends (Add to shares)
            if stock_div_dollar != 0:
                # Based on shares AFTER contribution? 
                # Methodology says "Calculated based on held shares... Reinvestment at average price"
                # Stock dividends are usually processed at Par.
                ratio = stock_div_dollar / 10.0
                current_shares *= (1.0 + ratio)

            # 4. Apply Split Adjustment (Manual logic for non-adjusted stocks)
            detector = _get_detector()
            if detector and stock_code and not is_pre_adjusted:
                ratio_now = detector.get_cumulative_ratio(stock_code, start_year, year)
                if i > 0:
                    ratio_prev = detector.get_cumulative_ratio(stock_code, start_year, sorted_years[i-1])
                    if ratio_prev != 0 and ratio_now != ratio_prev:
                        split_multiplier = ratio_now / ratio_prev
                        current_shares *= split_multiplier
            
            # Metric Calculation (current_shares are now adjusted for everything so far)
            total_asset_value = current_shares * p_end
            
            # Use actual investment duration, not global start year
            effective_start_year = sorted_years[0]
            n_yrs = year - effective_start_year + 1
            
            cagr_val = 0.0
            roi_val = 0.0
            
            if total_invested_cash > 0 and total_asset_value > 0:
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
                # Total Investment (Inclusive of Start Year)
                # Principal + (Number of Contribution Years * Contribution)
                total_investment = principal + (len(sorted_years) * annual_investment)
                results["finalValue"] = round(total_asset_value, 0)
                results["totalCost"] = round(total_investment, 0)
                
                # Recalculate ROI and CAGR for final results
                results["roi"] = ((total_asset_value - total_investment) / total_investment) * 100 if total_investment > 0 else 0
                n_years = len(sorted_years)
                if n_years > 0:
                    results["cagr"] = ((total_asset_value / principal) ** (1 / n_years) - 1) * 100 if principal > 0 else 0
                
        results[f"s{start_year}e{sorted_years[-1]}yrs"] = len(sorted_years)
        results["history"] = history
        return results

    def calculate_yearly_cumulative_cagr(self, df: Any, start_year: int):
        import pandas as pd
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
        # Ensure year column matches logic in other methods
        if 'year' not in df.columns and isinstance(df.index, pd.DatetimeIndex):
             years = df.index.year.unique()
        elif 'year' in df.columns:
             years = df['year'].unique()
        else:
             return {}
        
        for year in years:
            if year <= start_year:
                continue
                
            # Get the last available price for that year
            if isinstance(df.index, pd.DatetimeIndex):
                year_data = df[df.index.year == year]
            else:
                year_data = df[df['year'] == year]

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
        # Use last year from loop or years array
        last_year = years[-1] if len(years) > 0 else start_year
        results[f"s{start_year}e{last_year}yrs"] = duration
            
        return results
