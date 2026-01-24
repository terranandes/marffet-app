import requests
import json

try:
    url = "http://localhost:8000/api/race-data?start_year=2006&principal=1000000&contribution=60000"
    print(f"Fetching {url}...")
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        print(f"Got {len(data)} records.")
        if data:
            print("First Record:", json.dumps(data[0], indent=2))
            
            # Check for non-zero CAGR
            non_zero = [d for d in data if d.get('cagr', 0) != 0]
            print(f"Records with non-zero CAGR: {len(non_zero)}")
            if non_zero:
                print("Sample Non-Zero:", non_zero[0])
    else:
        print(f"Error: {res.status_code} {res.text}")
except Exception as e:
    print(e)
