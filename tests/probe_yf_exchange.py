import yfinance as yf

def probe():
    tickers = ["2330.TW", "6238.TW", "3174.TW"]
    for t in tickers:
        print(f"--- Probing {t} ---")
        try:
            dat = yf.Ticker(t).history(period="1mo")
            if not dat.empty:
                print(f"  FOUND! Rows: {len(dat)}")
                print(dat.tail(1))
            else:
                print("  Empty (Not Valid)")
        except Exception as e:
            print(f"  Error: {e}")

probe()
