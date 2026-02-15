import asyncio
import httpx
import json

async def probe_fmnptk(code):
    print(f"🔍 Probing FMNPTK for {code}...")
    url = "https://www.twse.com.tw/rwd/zh/afterTrading/FMNPTK"
    params = {"response": "json", "stockNo": code}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        data = resp.json()
        
        if 'data' not in data:
            print(f"❌ No data for {code}: {data.get('stat')}")
            return
            
        fields = data['fields']
        print(f"Fields: {fields}")
        
        for row in data['data'][-10:]:
            print(f"  {row}")

if __name__ == "__main__":
    asyncio.run(probe_fmnptk('2330'))
    asyncio.run(probe_fmnptk('4763'))
