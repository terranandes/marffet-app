
import requests
import json
import time

def probe_twse_2006():
    # Target: TSMC (2330) in Jan 2006
    # Expectation: Price ~60 NTD (Unadjusted)
    # yfinance gave ~29 NTD (Adjusted)
    
    url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
    params = {
        "response": "json",
        "date": "20060101",
        "stockNo": "2330"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"Probing {url} with {params}...")
    try:
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code != 200:
            print(f"Error: {resp.status_code}")
            return
            
        data = resp.json()
        if data.get('stat') != 'OK':
            print(f"API Error: {data.get('stat')}")
            return
            
        # Parse fields
        # Fields: ["Date", "Trade Volume", "Trade Value", "Opening Price", "Highest Price", "Lowest Price", "Closing Price", ...]
        fields = data.get('fields', [])
        print(f"Fields: {fields}")
        
        # Check first trading day
        first_day = data['data'][0]
        print(f"First Trading Day 2006: {first_day}")
        
        # Extract Closing Price
        # Date is usually Minguo (95/01/02)
        date_str = first_day[0]
        open_price = first_day[3]
        close_price = first_day[6]
        
        print(f"\nRESULTS:")
        print(f"Date: {date_str}")
        print(f"Open: {open_price}")
        print(f"Close: {close_price}")
        
        if float(open_price.replace(',', '')) > 50:
            print("SUCCESS: Price > 50 implies UNADJUSTED data!")
        else:
            print("FAILURE: Price < 50 implies ADJUSTED data (or split happened earlier).")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    probe_twse_2006()
