import httpx
import asyncio

async def probe_endpoint():
    # Base URL inferred from /v1/DailyQuotes redirect attempts, but Swagger paths are relative to server.
    # Swagger 'servers' key showed what? I printed keys but not content.
    # Assuming https://www.tpex.org.tw/openapi/v1
    
    url = "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes"
    
    # Test Params
    tests = [
        ("d=1130105", {"d": "1130105", "l": "zh-tw"}),
        ("d=113/01/05", {"d": "113/01/05", "l": "zh-tw"}),
        ("d=20240105", {"d": "20240105", "l": "zh-tw"}),
        ("d=1130102", {"d": "1130102", "l": "zh-tw"}), # Jan 2
    ]
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    async with httpx.AsyncClient(verify=False) as client:
        for name, params in tests:
            print(f"\n--- Testing {name} ---")
            try:
                resp = await client.get(url, params=params, headers=headers, timeout=10.0)
                print(f"Status: {resp.status_code}")
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"Data Type: {type(data)}")
                    if isinstance(data, list):
                        print(f"Len: {len(data)}")
                        # Find 6640
                        found = False
                        for item in data[:5]: # Print first 5
                             print(f"Sample: {item}")
                        
                        for item in data:
                             # Code usually "SecuritiesCompanyCode" or "Code"?
                             # Check keys in sample
                             if "6640" in str(item.values()):
                                 print(f"Found 6640: {item}")
                                 found = True
                                 break
                        if not found:
                             print("6640 Not Found in List")
            except Exception as e:
                print(f"Err: {e}")

if __name__ == "__main__":
    asyncio.run(probe_endpoint())
