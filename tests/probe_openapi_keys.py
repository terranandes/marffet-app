import httpx
import asyncio

async def probe_openapi_keys():
    url = "https://www.tpex.org.tw/openapi/v1/bond_cb_daily"
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.get(url, headers=headers)
        data = resp.json()
        if data:
            print(f"Full Keys: {data[0].keys()}")
            print(f"Full Item: {data[0]}")

if __name__ == "__main__":
    asyncio.run(probe_openapi_keys())
