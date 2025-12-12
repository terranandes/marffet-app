import httpx
import asyncio

async def probe_cb_csv():
    # Candidates for CSV
    candidates = [
        # 1. T59 CSV
        {
            "url": "https://www.tpex.org.tw/web/bond/trade_stat/convertible_bond_cny/t59.php",
            "params": {"l": "zh-tw", "d": "112/06/01", "o": "csv"},
            "desc": "T59 CSV"
        },
        # 2. CTPCNY CSV
        {
            "url": "https://www.tpex.org.tw/web/bond/trade_stat/convertible_bond_cny/ctpcny.php",
            "params": {"l": "en-us", "d": "112/06/01", "o": "csv"},
            "desc": "CTPCNY CSV"
        }
    ]
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for c in candidates:
            try:
                print(f"--- Probing {c['desc']} ---")
                resp = await client.get(c['url'], params=c.get('params'), headers=headers, timeout=10.0)
                print(f"Status: {resp.status_code}")
                ct = resp.headers.get("Content-Type", "")
                print(f"Content-Type: {ct}")
                
                if "text/csv" in ct or "application/csv" in ct or "ms-excel" in ct:
                    print(f"SUCCESS: Headers imply CSV/Excel!")
                    print(f"Snippet: {resp.text[:200]}")
                else:
                    if len(resp.text) < 1000:
                         print(f"Is 404 Page? {'404' in resp.text}")
                    else:
                         # Check if CSV-like (comma separated)
                         lines = resp.text.splitlines()
                         if len(lines) > 0 and "," in lines[0]:
                             print("Content looks like CSV!")
                             print(f"Line 1: {lines[0]}")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(probe_cb_csv())
