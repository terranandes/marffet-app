import httpx
import asyncio

async def inspect():
    url = "https://www.tpex.org.tw/openapi/swagger.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    async with httpx.AsyncClient(verify=False) as client:
        print("Fetching swagger.json...")
        resp = await client.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            path = "/tpex_mainboard_daily_close_quotes"
            if path in data['paths']:
                print(f"Path: {path}")
                op = data['paths'][path].get('get', {})
                params = op.get('parameters', [])
                print("Parameters:")
                for p in params:
                    print(f"  Name: {p.get('name')}, In: {p.get('in')}, Desc: {p.get('description')}")
            else:
                print(f"Path {path} NOT FOUND in swagger.")
        else:
            print(f"Error {resp.status_code}")

if __name__ == "__main__":
    asyncio.run(inspect())
