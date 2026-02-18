
import pandas as pd
import yfinance as yf
from pathlib import Path
import os

# Load stock list (simulate service logic)
base_dir = Path.home() / "github/martian/app"
csv_path = base_dir / "project_tw/stock_list.csv"
if not csv_path.exists():
    print(f"Error: {csv_path} not found")
    exit(1)

df = pd.read_csv(csv_path, dtype={'code': str}, nrows=50) # First 50
chunk = [f"{str(code).strip()}.TW" for code in df['code']]
print(f"Testing chunk of {len(chunk)} stocks.")
print(f"First: {chunk[0]}")

print("Downloading 2000-2004...")
# Same params as service V3
data = yf.download(chunk, start="2000-01-01", end="2004-01-01", group_by='ticker', actions=True, auto_adjust=False, progress=False)

print("\n--- Result ---")
print(f"Empty? {data.empty}")
print(f"Columns type: {type(data.columns)}")

if isinstance(data.columns, pd.MultiIndex):
    print(f"Columns levels: {data.columns.nlevels}")
    print(f"Level names: {data.columns.names}")
    
    # Try accessing 1101.TW
    target = "1101.TW"
    try:
        if target in data.columns.get_level_values(0):
            sub = data.xs(target, axis=1, level=0, drop_level=True)
            print(f"Successfully accessed {target}")
            print(sub.head())
            print(f"Rows: {len(sub)}")
        else:
            print(f"{target} NOT found in columns level 0.")
            print(f"Available tickers: {data.columns.get_level_values(0).unique()[:10]}")
    except Exception as e:
        print(f"Failed to access {target}: {e}")
else:
    print("Not MultiIndex.")
    print(data.columns)
