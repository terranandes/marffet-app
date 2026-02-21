import yfinance as yf
import pandas as pd

def test_1101_2000():
    ticker = "1101.TW"
    print(f"Downloading {ticker} for Jan 2000...")
    data = yf.download(
        [ticker],
        start="2000-01-01",
        end="2000-01-10",
        group_by='ticker',
        actions=True,
        auto_adjust=False,
        threads=False
    )
    print("\n--- Data ---")
    print(data)
    print("\n--- Columns ---")
    print(data.columns)
    
    # Check values
    if not data.empty:
        df = data.xs(ticker, axis=1, level=0) if isinstance(data.columns, pd.MultiIndex) else data
        print("\n--- Values ---")
        print(df[['Open', 'High', 'Low', 'Close', 'Volume']].head())

if __name__ == "__main__":
    test_1101_2000()
