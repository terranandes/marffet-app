
import httpx
import asyncio
import json

async def probe_cb_source():
    # Attempt 2: Check stk_quote_result (Main Board) for CBs (5 digits)
    url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php"
    params = {"l": "zh-tw", "o": "json"} 
    
    print(f"Probing {url} for 5-digit codes (CBs)...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote.php?l=zh-tw"
    }
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            resp = await client.get(url, params=params, headers=headers, timeout=10.0)
            data = resp.json()
            
            raw_rows = []
            if data.get('aaData'): raw_rows = data['aaData']
            elif data.get('tables'): 
                 for t in data['tables']: raw_rows.extend(t.get('data', []))
            
            cb_count = 0
            sample = None
            for row in raw_rows:
                if len(row) > 0:
                    code = row[0].strip()
                    if len(code) == 5 and code.isdigit():
                        cb_count += 1
                        if not sample: sample = row
                        
            print(f"Found {cb_count} 5-digit codes (Likely CBs).")
            if sample:
                print(f"Sample CB Row: {sample}")
                # Analyze columns for 'Premium Rate'?
                # Daily Close Quotes usually has: Code, Name, Close, Change, Open, High, Low, Vol... 
                # Does it have Premium? Probably NOT.
                pass
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(probe_cb_source())
