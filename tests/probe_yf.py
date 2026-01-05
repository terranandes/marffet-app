import yfinance as yf
import pandas as pd

def probe():
    print("Fetching 6640.TWO from YFinance...")
    try:
        # Fetch Jan 2024
        df = yf.download("6640.TWO", start="2024-01-01", end="2024-01-10", progress=False)
        print("Data Fetched:")
        print(df)
        
        if not df.empty:
            close = df['Close'].iloc[0]
            # Handle multi-level columns in newer yfinance
            if isinstance(close, pd.Series):
                val = close.iloc[0] # ?? depends on structure
                print(f"First Close: {val}")
            else:
                print(f"First Close: {close}")
                
            # Verify correctness
            # Should be ~150
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    probe()
