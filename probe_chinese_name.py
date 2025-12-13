import httpx
import asyncio

async def probe():
    # 5274 (ASPEED), 6640 (IunHua), 00909 (Cathay)
    targets = ["5274", "6640", "00909"]
    
    async with httpx.AsyncClient() as client:
        # MIS TWSE (Realtime) usually has names
        url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
        
        # Build query: ex_ch=tse_5274.tw|otc_6640.tw ...
        # Need to guess exchange. 
        # 5274 is TPEx (OTC)? (ASPEED is 4-digit, usually TPEx for semis?)
        # Let's try both tse and otc
        
        query_list = []
        for t in targets:
            query_list.append(f"tse_{t}.tw")
            query_list.append(f"otc_{t}.tw")
            
        params = {"ex_ch": "|".join(query_list), "json": "1", "delay": "0"}
        
        print(f"Querying MIS: {params['ex_ch']}")
        try:
            resp = await client.get(url, params=params, timeout=10)
            data = resp.json()
            if 'msgArray' in data:
                for msg in data['msgArray']:
                    c = msg.get('c') # Code
                    n = msg.get('n') # Name
                    ex = msg.get('ex') # Exchange
                    print(f"  Found {c} ({ex}): {n}")
            else:
                print("No msgArray in response.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(probe())
