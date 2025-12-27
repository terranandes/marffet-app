import yfinance as yf
import pandas as pd

ticker = "8299.TWO" # Phison
start = "2006-01-01"
end = "2006-12-31"

print(f"Fetching {ticker} from {start} to {end}...")
t = yf.Ticker(ticker)
hist = t.history(start=start, end=end, actions=True)
print("Shape:", hist.shape)
print("Columns:", hist.columns)
if not hist.empty:
    print(hist.head())
    print("Dividends sum:", hist['Dividends'].sum())
else:
    print("Empty history.")
