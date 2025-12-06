
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
