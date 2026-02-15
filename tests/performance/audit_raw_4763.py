import httpx
import asyncio
import json

async def check_raw_4763():
    print("🔍 Fetching Raw TWT49U for 4763 in 2023...")
    url = 'https://www.twse.com.tw/exchangeReport/TWT49U?response=json&startDate=20230101&endDate=20231231'
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=20.0)
        data = resp.json()
        
        if 'data' not in data:
            print("❌ No data found.")
            print(data)
            return
            
        found = False
        for i, row in enumerate(data['data']):
            if row[1] == '4763':
                print(f"Row {i}: {row}")
                found = True
        
        if not found:
            print("❌ 4763 not found in 2023 TWT49U.")

if __name__ == "__main__":
    asyncio.run(check_raw_4763())
