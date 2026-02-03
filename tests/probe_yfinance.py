
import yfinance as yf
import pandas as pd

def probe_yfinance_unadjusted():
    print("Fetching TSMC (2330.TW) 2006 with auto_adjust=False...")
    
    # Try different combinations
    # 1. auto_adjust=False
    ticker = yf.Ticker("1101.TW")
    hist = ticker.history(start="2006-01-01", end="2006-02-01", auto_adjust=False)
    
    if not hist.empty:
        first = hist.iloc[0]
        print("\n--- Result (auto_adjust=False) ---")
        print(f"Date: {first.name}")
        print(f"Open: {first['Open']}")
        print(f"Close: {first['Close']}")
        print(f"Adj Close: {first.get('Adj Close', 'N/A')}")
        
    else:
        print("No data found.")

if __name__ == "__main__":
    probe_yfinance_unadjusted()
