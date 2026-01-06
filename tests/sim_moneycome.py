import json
import os

# Configuration matching User's screenshot
PRINCIPAL = 1_000_000
ANNUAL_CONTRIB = 60_000
START_YEAR = 2006
END_YEAR = 2025 # Screenshot says 2026, but usually data is up to last closed year
STOCK_ID = "2330"

# Dividend Data (Cash per Share)
DIVIDENDS = {
    2006: 2.39, 2007: 2.95, 2008: 2.99, 2009: 2.98, 2010: 3.00,
    2011: 3.00, 2012: 3.00, 2013: 3.00, 2014: 3.00, 2015: 4.50,
    2016: 6.00, 2017: 7.00, 2018: 8.00, 2019: 12.5, 2020: 10.0,
    2021: 10.5, 2022: 11.0, 2023: 11.5, 2024: 15.0, 2025: 19.0
}

def get_price(year, type='start'):
    # Load JSON
    try:
        path = f"data/raw/Market_{year}_Prices.json"
        if not os.path.exists(path):
            return None
        with open(path, 'r') as f:
            data = json.load(f)
            if STOCK_ID in data:
                return data[STOCK_ID].get(type)
    except Exception as e:
        print(e)
    return None

def run_simulation():
    total_shares = 0
    total_cash_invested = 0
    
    print(f"{'Year':<6} {'Price(S)':<10} {'Price(E)':<10} {'Shares':<10} {'Value':<12} {'DivCash':<10}")
    print("-" * 65)

    # Initial Purchase (2006 Start)
    start_price_2006 = get_price(2006, 'start')
    total_shares = PRINCIPAL / start_price_2006
    total_cash_invested += PRINCIPAL
    
    print(f"INIT   {start_price_2006:<10} {'-':<10} {int(total_shares):<10} {int(total_shares * start_price_2006):<12} {'-':<10}")

    for year in range(START_YEAR, END_YEAR + 1):
        start_price = get_price(year, 'start')
        end_price = get_price(year, 'end')
        
        # Assumption: Dividends received used to buy more shares at AVG price (or Start?)
        # MoneyCome says "Yearly Cash Div. Reinvestment" -> buying at "Yearly Avg"? 
        # Let's approx with (Start + End) / 2
        avg_price = (start_price + end_price) / 2
        
        # 1. Receive Dividend
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
        
        print(f"{year:<6} {start_price:<10} {end_price:<10} {int(total_shares):<10} {int(wealth):<12} {int(total_div_cash):<10}")

    print("-" * 65)
    print(f"Final Shares: {int(total_shares)}")
    print(f"Final Value: {int(total_shares * end_price)}")
    
if __name__ == "__main__":
    run_simulation()
