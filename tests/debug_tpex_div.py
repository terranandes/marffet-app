import httpx
import asyncio

async def probe_tpex_div():
    # Target: TPEX Ex-Rights Result
    # URL: https://www.tpex.org.tw/web/stock/exright/daily/daily_result.php
    # Params: d=112/06/01 (ROC Date), l=zh-tw, o=json
    
    base_url = "https://www.tpex.org.tw/web/stock/exright/daily/daily_result.php"
    
    # Try a month range? TPEX APIs usually take 'd' as a specific date, or sometimes YYYY/MM for month?
    # Let's try a specific date first that is likely to have dividends (June/July/Aug).
    # Year 112 (2023), July (07).
    
    # Try Date: 112/07/04 (Tuesday)
    params_date = {
        "l": "zh-tw",
        "o": "json",
        "d": "112/07/06" 
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.tpex.org.tw/"
    }
    
    async with httpx.AsyncClient() as client:
        print(f"Probing Date: {params_date['d']}...")
        try:
            resp = await client.get(base_url, params=params_date, headers=headers)
            print(f"Status: {resp.status_code}")
            try:
                data = resp.json()
                print("Response JSON Keys:", data.keys())
                
                aaData = data.get('aaData', [])
                if aaData:
                    print(f"aaData Count: {len(aaData)}")
                    print("Sample Row:", aaData[0])
                else:
                    print("aaData is empty.")
                    
            except Exception as e:
                print(f"JSON Parse Error: {e}")
                print("Text content:", resp.text[:200])

        except Exception as e:
            print(f"Request Error: {e}")
            
    # Probe 2: Try Year/Month only? '112/07'
    print("-" * 30)
    params_month = {
        "l": "zh-tw",
        "o": "json",
        "d": "112/07"
    }
    async with httpx.AsyncClient() as client:
        print(f"Probing Month: {params_month['d']}...")
        try:
            resp = await client.get(base_url, params=params_month, headers=headers)
            print(f"Status: {resp.status_code}")
            try:
                data = resp.json()
                if 'aaData' in data and len(data['aaData']) > 0:
                    print(f"Success! Found {len(data['aaData'])} items for Month.")
                    print("Sample:", data['aaData'][0])
                else:
                    print("Month specific probe returned empty.")
            except:
                pass
        except:
            pass

if __name__ == "__main__":
    asyncio.run(probe_tpex_div())
