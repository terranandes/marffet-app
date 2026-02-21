import yfinance as yf
import pandas as pd

def test_columns():
    ticker = "1101.TW"
    print(f"Downloading {ticker}...")
    data = yf.download(
        [ticker],
        start="2024-01-01",
        end="2024-01-10",
        group_by='ticker',
        actions=True,
        auto_adjust=False,
        threads=False
    )
    print("\n--- Data ---")
    print(data)
    print("\n--- Columns ---")
    print(data.columns)
    
    if isinstance(data.columns, pd.MultiIndex):
        print("\n--- Level 0 check ---")
        if ticker in data.columns.get_level_values(0):
            df = data.xs(ticker, axis=1, level=0)
            print("\n--- XS Structure ---")
            print(df.columns)
            p_cols = [c for c in df.columns if c in ['Open', 'High', 'Low', 'Close', 'Volume']]
            print(f"p_cols: {p_cols}")

if __name__ == "__main__":
    test_columns()
