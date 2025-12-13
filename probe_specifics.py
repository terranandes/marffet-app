import yfinance as yf
import pandas as pd

def probe():
    # 3147.TWO (Likely) or 3147.TW
    # 6238.TWO (Likely) or 6238.TW
    tickers = ["3147.TWO", "3147.TW", "6238.TWO", "6238.TW"]
    
    print("--- Probing YFinance ---")
    for t in tickers:
        try:
            dat = yf.Ticker(t).history(period="1mo")
            if not dat.empty:
                print(f"FOUND {t}: Last Price {dat['Close'].iloc[-1]}")
            else:
                print(f"NOT FOUND {t} (Empty/Delisted)")
        except Exception as e:
            print(f"Error {t}: {e}")

    # Check Excel for 3147
    print("\n--- Checking Excel for 3147 ---")
    try:
        df = pd.read_excel('project_tw/output/stock_list_s2006e2025_unfiltered.xlsx')
        df['id'] = df['id'].astype(str)
        row = df[df['id'] == '3147']
        if not row.empty:
            print(row[['id', 'name', 'cagr_pct', 'volatility_pct', 'valid_years']].to_string())
        else:
            print("3147 NOT IN unfiltered list.")
    except Exception as e:
        print(f"Excel Error: {e}")

if __name__ == "__main__":
    probe()
