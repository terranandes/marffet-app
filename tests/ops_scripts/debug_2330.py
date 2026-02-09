import yfinance as yf
import pandas as pd
import math

def _is_valid_number(value) -> bool:
    if value is None:
        return False
    if isinstance(value, float):
        return not (math.isnan(value) or math.isinf(value))
    return True

def main():
    ticker = "2330.TW"
    print(f"Downloading {ticker}...")
    
    # Same params as crawl_fast.py
    df = yf.download(ticker, start="2024-01-01", end="2024-12-31", progress=False, auto_adjust=False, threads=False)
    
    print(f"Shape: {df.shape}")
    print(df.head())
    
    if df.empty:
        print("❌ Empty DataFrame!")
        return

    # Simulation of process_to_cache
    print("\nSimulating process_to_cache...")
    
    # Ensure index is datetime
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    daily = []
    
    # Check column structure
    print(f"Columns: {df.columns}")
    
    for idx, row in df.iterrows():
        # Handle MultiIndex columns if present
        try:
            o = row['Open'].iloc[0] if isinstance(row['Open'], pd.Series) else row['Open']
            h = row['High'].iloc[0] if isinstance(row['High'], pd.Series) else row['High']
            l = row['Low'].iloc[0] if isinstance(row['Low'], pd.Series) else row['Low']
            c = row['Close'].iloc[0] if isinstance(row['Close'], pd.Series) else row['Close']
            v = row['Volume'].iloc[0] if isinstance(row['Volume'], pd.Series) else row['Volume']
        except Exception as e:
            # Fallback for simple index
            o = row['Open']
            h = row['High']
            l = row['Low']
            c = row['Close']
            v = row['Volume']

        # debug first row
        if len(daily) == 0:
            print(f"Row 1 Raw: o={o}, h={h}, l={l}, c={c}, v={v}")
            print(f"Row 1 types: {type(o)}, {type(h)}, {type(l)}, {type(c)}, {type(v)}")

        # Skip if any OHLC is invalid (NaN/None)
        if not all(_is_valid_number(float(x)) for x in [o, h, l, c]):
            # print(f"Skipping invalid row {idx}")
            continue
            
        daily.append({
            "d": idx.strftime("%Y-%m-%d"),
            "c": c
        })
        
    print(f"Valid Daily Rows: {len(daily)}")
    
    if len(daily) == 0:
        print("❌ All rows filtered out!")
    else:
        print("✅ Data passed filter!")

if __name__ == "__main__":
    main()
