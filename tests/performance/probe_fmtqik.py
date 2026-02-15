import asyncio
import httpx
import json

async def probe_fmtqik(code):
    print(f"🔍 Probing FMTQIK for {code}...")
    url = "https://www.twse.com.tw/exchangeReport/FMTQIK"
    params = {"response": "json", "stockNo": code}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        data = resp.json()
        
        if 'data' not in data:
            print(f"❌ No data for {code}: {data.get('stat')}")
            return
            
        fields = data['fields']
        print(f"Fields: {fields}")
        
        # Open prices are often not in FMTQIK, but High/Low/Close are.
        # Let's see the last 5 years
        for row in data['data'][-5:]:
            print(f"  {row}")

if __name__ == "__main__":
    asyncio.run(probe_fmtqik('2330'))
    asyncio.run(probe_fmtqik('4763'))
