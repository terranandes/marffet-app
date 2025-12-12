import asyncio
import httpx
import json
import os

async def fix_6669_2019():
    print("--- Fixing 6669 2019 Data ---")
    
    # 1. Fix Price Start
    print("Fixing Start Price...")
    prices_file = "data/raw/Market_2019_Prices.json"
    if os.path.exists(prices_file):
        with open(prices_file, 'r') as f:
            data = json.load(f)
            
        if '6669' in data:
            print(f"Current: {data['6669']}")
            # Force Fetch
            async with httpx.AsyncClient() as client:
                # Scan Monthly
                found_price = 0.0
                for m in range(1, 13):
                    date_str = f"2019{m:02d}01"
                    url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
                    params = {"response": "json", "date": date_str, "stockNo": "6669"}
                    try:
                        print(f"Scanning {date_str}...")
                        resp = await client.get(url, params=params, timeout=5.0)
                        d = resp.json()
                        if d['stat'] == 'OK':
                            # Get First Row
                            rows = d['data']
                            if rows:
                                # Row: date, vol, amt, OPEN, ...
                                op = float(rows[0][3].replace(',', ''))
                                print(f"Found First Open: {op} on {rows[0][0]}")
                                found_price = op
                                break
                        await asyncio.sleep(1)
                    except Exception as e:
                        print(f"Err {date_str}: {e}")
                
                if found_price > 0:
                    data['6669']['start'] = found_price
                    with open(prices_file, 'w') as f:
                        json.dump(data, f)
                    print("Price Updated.")
        else:
            print("6669 not in cache?!")
    else:
        print("Price Cache Missing")

    # 2. Fix Dividend
    print("\nFixing Dividend...")
    div_file = "data/raw/TWT49U_2019.json"
    
    # Always fetch fresh
    url = "https://www.twse.com.tw/exchangeReport/TWT49U"
    params = {
        "response": "json",
        "strDate": "20190101",
        "endDate": "20191231"
    }
    async with httpx.AsyncClient() as client:
        print("Fetching TWT49U 2019 Monthly...")
        combined_rows = []
        for m in range(1, 13):
            s_date = f"2019{m:02d}01"
            # Get EOM
            if m == 2:
                e_date = f"2019{m:02d}28"
            elif m in [4, 6, 9, 11]:
                e_date = f"2019{m:02d}30"
            else:
                e_date = f"2019{m:02d}31"
                
            params = {
                "response": "json",
                "strDate": s_date,
                "endDate": e_date
            }
            try:
                await asyncio.sleep(0.5)
                print(f"  Fetching {s_date}-{e_date}...")
                resp = await client.get(url, params=params, timeout=10.0)
                data = resp.json()
                if data['stat'] == 'OK':
                     rows = data.get('data', [])
                     print(f"    Got {len(rows)} rows.")
                     combined_rows.extend(rows)
                else:
                     print(f"    Stat: {data.get('stat')} | Title: {data.get('title')}")
            except Exception as e:
                print(f"Err {m}: {e}")
        
        # Save Combined
        print(f"Total rows: {len(combined_rows)}")
        final_data = {"stat": "OK", "date": "2019", "title": "Yearly", "data": combined_rows}
        with open(div_file, 'w') as f:
            json.dump(final_data, f)
            
        # Check 6669
        for r in combined_rows:
            if '6669' in str(r):
                print(f"Found 6669 Div: {r}")

if __name__ == "__main__":
    asyncio.run(fix_6669_2019())
