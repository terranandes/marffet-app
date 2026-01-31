import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


import httpx
import asyncio
import yfinance as yf

async def main():
    print("\n--- Probe 8: Ticker Debug ---")
    
    async def probe_yf(ticker):
        try:
            print(f"Fetching {ticker}...")
            dat = await asyncio.to_thread(yf.download, ticker, period="1d", progress=False, auto_adjust=False)
            if not dat.empty:
                # Check column structure
                if isinstance(dat.columns, tuple):
                     print(f"SUCCESS {ticker}: {dat.iloc[-1]}")
                else:
                     val = dat['Close'].iloc[-1]
                     print(f"SUCCESS {ticker}: {val}")
            else:
                print(f"FAIL {ticker}: Empty")
        except Exception as e:
            print(f"ERROR {ticker}: {e}")

    await probe_yf("6533.TWO")
    await probe_yf("6533.TW")
    await probe_yf("65331.TWO")
    await probe_yf("65331.TW")
    await probe_yf("2330.TW") # Control

if __name__ == "__main__":
    asyncio.run(main())
