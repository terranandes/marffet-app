
import asyncio
import pandas as pd
from app.services.market_data_provider import MarketDataProvider
from app.services.roi_calculator import _get_detector

# Configuration matching User's screenshot
PRINCIPAL = 1_000_000
ANNUAL_CONTRIB = 0
START_YEAR = 2006
END_YEAR = 2025
STOCK_ID = "2330"

async def run_simulation():
    # 1. Fetch Data
    prices_df = MarketDataProvider.get_all_daily_history_df("2006-01-01")
    df = prices_df[prices_df['stock_id'] == STOCK_ID].copy()
    df['year'] = df['date'].dt.year
    
    divs_df = MarketDataProvider.get_all_dividends_df(2006)
    stock_divs = divs_df[divs_df['stock_id'] == STOCK_ID]
    
    DIVIDENDS = {}
    for _, row in stock_divs.iterrows():
        DIVIDENDS[int(row['year'])] = float(row['cash'])

    total_shares = 0
    total_cash_invested = 0
    
    print(f"{'Year':<6} {'Price(S)':<10} {'Price(E)':<10} {'Shares':<10} {'Value':<12} {'DivCash':<10}")
    print("-" * 65)

    # Initial Purchase (2006 Start)
    year_data_2006 = df[df['year'] == 2006]
    start_price_2006 = year_data_2006.iloc[0]['open']
    total_shares = PRINCIPAL / start_price_2006
    total_cash_invested += PRINCIPAL
    
    print(f"INIT   {start_price_2006:<10.2f} {'-':<10} {int(total_shares):<10} {int(total_shares * start_price_2006):<12} {'-':<10}")

    for year in range(START_YEAR, END_YEAR + 1):
        year_data = df[df['year'] == year]
        if year_data.empty: continue
        
        start_price = year_data.iloc[0]['open']
        end_price = year_data.iloc[-1]['close']
        avg_price = (start_price + end_price) / 2
        
        # 1. Receive Dividend (On carry-over shares)
        div_per_share = DIVIDENDS.get(year, 0)
        total_div_cash = total_shares * div_per_share
        
        # 2. Reinvest Dividend
        new_shares_div = total_div_cash / avg_price
        
        # 3. Annual Contribution
        new_shares_contrib = ANNUAL_CONTRIB / avg_price
        total_cash_invested += ANNUAL_CONTRIB
        
        # Update Totals
        total_shares += (new_shares_div + new_shares_contrib)
        
        # Value at End of Year
        wealth = total_shares * end_price
        
        print(f"{year:<6} {start_price:<10.2f} {end_price:<10.2f} {int(total_shares):<10} {int(wealth):<12} {int(total_div_cash):<10}")

    print("-" * 65)
    print(f"Final Shares: {int(total_shares)}")
    print(f"Final Value: {int(total_shares * end_price)}")
    print(f"Total Invested: {total_cash_invested}")
    years = END_YEAR - START_YEAR + 1
    cagr = ((total_shares * end_price) / PRINCIPAL)**(1/years) - 1
    print(f"CAGR: {cagr*100:.2f}%")

if __name__ == "__main__":
    asyncio.run(run_simulation())
