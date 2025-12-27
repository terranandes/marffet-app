import httpx
import asyncio

async def probe():
    url = "https://www.twse.com.tw/exchangeReport/FMTQIK"
    stock = "3174"
    
    async with httpx.AsyncClient() as client:
        print(f"--- Probing FMTQIK for {stock} ---")
        params = {"response": "json", "stockNo": stock}
        try:
            resp = await client.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get('stat') == 'OK':
                print("  FOUND in TWSE FMTQIK!")
                print("  Data:", data.get('data')[:2]) # Show first 2 years
            else:
                print("  NOT FOUND in FMTQIK. Stat:", data.get('stat'))
        except Exception as e:
            print(f"  Error: {e}")

asyncio.run(probe())
