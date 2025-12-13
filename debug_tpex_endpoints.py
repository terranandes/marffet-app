import httpx
import asyncio

async def probe_endpoints():
    # Valid st43 logic?
    # Referer is key?
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43.php?l=zh-tw"
    }
    
    url_quote = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
    
    tests = [
        ("Quote (113/01/05)", url_quote, {"l": "zh-tw", "d": "113/01/05", "o": "json"}),
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43.php?l=zh-tw",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # Session approach
    async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
        # 1. Hit Valid Page to get Cookies
        # print("Fetching st43.php for cookies...")
        # await client.get("https://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43.php?l=zh-tw", headers=headers)
        
        for name, url, p in tests:
            print(f"\nTesting {name}...")
            # Add timestamp to mitigate cache/blocking? & _=TIMESTAMP
            # p['_'] = int(asyncio.get_event_loop().time() * 1000)
            
            try:
                resp = await client.get(url, params=p, headers=headers)
                print(f"Status: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"Final URL: {resp.url}")
                    if "errors" in str(resp.url):
                        print("Redirected to Errors")
                        continue
                        
                    try:
                         data = resp.json()
                         print(f"Keys: {data.keys()}")
                         print(f"Stat: {data.get('st43_result', {}).get('stat') if 'st43_result' in data else data.get('stat')}")
                         
                         aaData = data.get('aaData') 
                         if not aaData:
                             aaData = data.get('st43_result', {}).get('aaData')
                         
                         print(f"Data Len: {len(aaData) if aaData else 0}")
                         if aaData:
                             print(f"Sample: {aaData[0]}")
                             
                         # Check Tables
                         tables = data.get('tables', [])
                         if tables:
                             print(f"Tables Found: {len(tables)}")
                             for i, t in enumerate(tables):
                                 t_data = t.get('data', [])
                                 print(f"  Table {i} Title: {t.get('title')} - Rows: {len(t_data)}")
                                 if t_data:
                                     print(f"  Table {i} Sample: {t_data[0]}")
                    except Exception as je:
                        print(f"JSON Error: {je}")
                        print(f"Text: {resp.text[:100]}")
            except Exception as e:
                print(f"Err: {e}")

if __name__ == "__main__":
    asyncio.run(probe_endpoints())
