import httpx
import asyncio

async def probe_cb_html():
    url = "https://www.tpex.org.tw/web/bond/trade_stat/convertible_bond_cny/t59.php"
    params = {"l": "zh-tw", "d": "112/06/01"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            print(f"Fetching {url}...")
            resp = await client.get(url, params=params, headers=headers, timeout=15.0)
            print(f"Status: {resp.status_code}")
            content = resp.text
            print(f"Length: {len(content)}")
            
            # Check for 65331 (Sample CB)
            if "65331" in content:
                print("SUCCESS: Found '65331' in HTML!")
            else:
                print("FAILURE: '65331' NOT found.")
                # Print snippet
                print("Snippet:")
                print(content[:500])
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(probe_cb_html())
