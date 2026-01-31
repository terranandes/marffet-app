import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import yfinance as yf

def test_batch():
    tickers = ["6640.TWO", "006201.TWO", "5274.TWO"] # 6640, 006201, 5274 (Generic)
    print(f"Fetching {tickers}...")
    
    # auto_adjust=False for Raw Prices
    data = yf.download(tickers, start="2024-01-01", end="2024-01-05", auto_adjust=False, progress=False)
    
    print("Columns:", data.columns)
    # yfinance multi-index columns: (Price, Ticker)
    
    try:
        closes = data['Close']
        print("\nCloses:")
        print(closes)
        
        # Check specific values
        # 6640 Raw Close Jan 2
        p6640 = closes['6640.TWO'].iloc[0]
        print(f"6640 Jan 2 Raw: {p6640}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_batch()
