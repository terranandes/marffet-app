import httpx
import asyncio
import re

async def probe_content():
    url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43.php?l=zh-tw"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.tpex.org.tw/"
    }
    
    async with httpx.AsyncClient(verify=False) as client:
        print("Fetching st43.php...")
        resp = await client.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        
        text = resp.text
        # Search for .php links
        phps = re.findall(r'[\w\-]+\.php', text)
        print(f"PHP Files Found: {set(phps)}")
        
        # Search for form action
        forms = re.findall(r'<form.*?>', text, re.DOTALL)
        print(f"Forms: {forms}")
        
        # Search for AJAX
        # ajax call often has url: '...'
        ajax_urls = re.findall(r"url\s*:\s*['\"](.*?)['\"]", text)
        print(f"AJAX URLs: {ajax_urls}")

if __name__ == "__main__":
    asyncio.run(probe_content())
