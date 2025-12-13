import asyncio
from project_tw.crawler_tpex import TPEXCrawler

async def verify():
    crawler = TPEXCrawler()
    print("Fetching TPEx 2024...")
    data = await crawler.fetch_market_prices_batch([2024])
    
    codes = ['6640', '006201']
    for c in codes:
        if 2024 in data and c in data[2024]:
            p = data[2024][c]
            print(f"{c} 2024: Start={p['start']}, End={p['end']}")

if __name__ == "__main__":
    asyncio.run(verify())
