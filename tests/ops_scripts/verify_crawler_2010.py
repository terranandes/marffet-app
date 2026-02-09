import asyncio
import httpx
from app.project_tw.crawler import TWSECrawler

async def test_crawler():
    crawler = TWSECrawler()
    # Test 2010 Jan (Start of data for new endpoint)
    # Date format for API is YYYYMMDD
    date_str = "20100101"
    stock_code = "2330"
    
    print(f"Testing crawler for {stock_code} on {date_str}...")
    
    async with httpx.AsyncClient() as client:
        # Mock semaphore
        sem = asyncio.Semaphore(1)
        data = await crawler.fetch_stock_month(client, stock_code, date_str, sem)
        
        if data and data.get('stat') == 'OK':
            print("✅ Fetch successful!")
            # Check first row for Open Price
            # Row format: [Date, Vol, Val, Open, High, Low, Close, ...]
            first_row = data['data'][0]
            print(f"First Row: {first_row}")
            open_price = first_row[3]
            print(f"Open Price: {open_price}")
            
            if float(open_price) > 60:
                print("✅ Price looks unadjusted (~65)")
            else:
                print("⚠️ Price looks suspicious (adjusted?)")
        else:
            print("❌ Fetch failed or no data.")
            print(data)

if __name__ == "__main__":
    asyncio.run(test_crawler())
