import yfinance as yf
import pandas as pd

def get_dividends(symbol):
    try:
        # Taiwan stock
        ticker = yf.Ticker(f"{symbol}.TW")
        divs = ticker.dividends
        print(f"--- {symbol} Dividends ---")
        # Filter 2006 to 2026
        # yfinance returns Series with DateTime index
        divs = divs[divs.index.year >= 2006]
        
        # Group by year
        annual_divs = divs.groupby(divs.index.year).sum()
        
        print(f"{'Year':<6} {'Div (TWD)':<10}")
        for year, amount in annual_divs.items():
            print(f"{year:<6} {amount:<10.2f}")
            
    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    get_dividends("2330")
