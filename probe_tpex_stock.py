import httpx
import asyncio

async def probe_tpex():
    # TPEx Daily Quote
    url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
    stock = "3174"
    date = "113/12/11" # Wed
    
    async with httpx.AsyncClient() as client:
        print(f"--- Probing TPEx for {stock} ---")
        # Try without se to get all sections? Or stick to EW.
        # Check crawler_tpex.py usage. It uses se=EW.
        # Maybe 3174 is NOT EW (Equity)? 
        # But Fitipower is equity.
        params = {"l": "en-us", "d": date, "o": "json"} 
        
        try:
            resp = await client.get(url, params=params, timeout=10)
            data = resp.json()
            # TPEx returns ALL stocks in one JSON usually?
            # Or filtering?
            # Usually it returns huge list.
            
            rows = data.get('aaData', [])
            print(f"  Total Rows: {len(rows)}")
            
            found = False
            for r in rows:
                # r[0] is Code
                if r[0] == stock:
                    print(f"  FOUND in TPEx! {r}")
                    found = True
                    break
            
            if not found:
                print(f"  NOT FOUND in TPEx")
                
        except Exception as e:
            print(f"  Error: {e}")

import asyncio
asyncio.run(probe_tpex())
