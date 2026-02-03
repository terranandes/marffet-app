
import requests
import json

def probe_tpex_2006():
    # Target: 8962 (Emerging/OTC) in 2006?
    # TPEx URL usually: https://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_result.php
    # Params: d=95/01 (Minguo Year/Month), stkno=8962
    
    # Minguo 95 = 2006
    url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_result.php"
    params = {
        "d": "95/01",
        "stkno": "8962",
        "l": "en" # English or 'zh-tw'
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    print(f"Probing TPEx {url} with {params}...")
    try:
        resp = requests.get(url, params=params, headers=headers)
        print(f"Status Code: {resp.status_code}")
        # print(f"Raw Text: {resp.text[:500]}...") # Peek first 500 chars
        
        try:
            data = resp.json()
            # Check integrity
            # Expected keys: "aaData", "stkTotal", "reportTitle"
            print(f"Response Keys: {data.keys()}")
            
            if "aaData" in data and len(data["aaData"]) > 0:
                first_day = data["aaData"][0]
                print(f"First Day 2006 Data: {first_day}")
                print("Success! TPEx Legacy Data found.")
            else:
                print("No data found in aaData.")
        except json.JSONDecodeError:
            print("Failed to decode JSON. Raw output:")
            print(resp.text[:1000]) # Print first 1000 chars to debug HTML/Error
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    probe_tpex_2006()
