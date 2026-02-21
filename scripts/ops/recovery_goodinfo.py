import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
import duckdb
import re

async def fetch_goodinfo_playwright(context, stock_id: str, sem: asyncio.Semaphore):
    url = f"https://goodinfo.tw/tw/StockBzPerformance.asp?STOCK_ID={stock_id}"
    
    async with sem:
        for attempt in range(3):
            page = await context.new_page()
            try:
                # Wait until network is idle or table appears
                await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                await page.wait_for_selector('#tblDetail', timeout=10000)
                
                content = await page.content()
                await page.close()
                return stock_id, content
            except Exception as e:
                await page.close()
                await asyncio.sleep(2)
        return stock_id, None

def parse_html(stock_id: str, html: str):
    records = []
    if not html: return records
    
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'id': 'tblDetail'})
    if not table: return records
    
    rows = table.find_all('tr', {'align': 'center'})
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 5: continue
        
        year_str = cols[0].text.strip()
        if not re.match(r'^20\d{2}$', year_str): continue
        year = int(year_str)
        if year < 2006: continue
        
        try:
            # Goodinfo Close/High/Low map
            # 3 = Open, 4 = High, 5 = Low, 6 = Close
            open_p = float(cols[3].text.replace(',', ''))
            high_p = float(cols[4].text.replace(',', ''))
            low_p = float(cols[5].text.replace(',', ''))
            close_p = float(cols[6].text.replace(',', ''))
            
            # Start and End bounds
            records.append({
                'stock_id': stock_id,
                'date': f"{year}-01-02",
                'open': open_p, 'high': open_p, 'low': open_p, 'close': open_p,
                'volume': 0, 'market': 'TWSE'
            })
            records.append({
                'stock_id': stock_id,
                'date': f"{year}-12-31",
                'open': close_p, 'high': close_p, 'low': close_p, 'close': close_p,
                'volume': 0, 'market': 'TWSE'
            })
        except:
            continue
    return records

async def main():
    con = duckdb.connect('data/market.duckdb')
    print("🗑️ Resetting DB...")
    con.execute("DELETE FROM daily_prices")
    
    ref_df = pd.read_excel('app/project_tw/references/stock_list_s2006e2026_unfiltered.xlsx')
    valid_tickers = ref_df['id'].astype(str).str.zfill(4).tolist()
    
    print(f"🚀 Playwright starting parallel browser extraction for {len(valid_tickers)} references...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use single context to share cookies that bypass client challenges
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 720}
        )
        
        sem = asyncio.Semaphore(5) # 5 concurrent browser tabs
        all_records = []
        
        tasks = [fetch_goodinfo_playwright(context, t, sem) for t in valid_tickers]
        
        chunk_size = 50
        for i in range(0, len(tasks), chunk_size):
            chunk_tasks = tasks[i:i+chunk_size]
            results = await asyncio.gather(*chunk_tasks)
            
            print(f"Processing chunk {i//chunk_size + 1} / {len(tasks)//chunk_size + 1}...")
            
            for sid, html in results:
                recs = parse_html(sid, html)
                all_records.extend(recs)
                
            await asyncio.sleep(1)
            
            if len(all_records) > 2000:
                temp_df = pd.DataFrame(all_records)
                temp_df = temp_df.drop_duplicates(subset=['stock_id', 'date'])
                con.register('temp_df', temp_df)
                con.execute("INSERT OR IGNORE INTO daily_prices SELECT * FROM temp_df")
                con.unregister('temp_df')
                all_records = []
                
        if all_records:
            temp_df = pd.DataFrame(all_records)
            temp_df = temp_df.drop_duplicates(subset=['stock_id', 'date'])
            con.register('temp_df', temp_df)
            con.execute("INSERT OR IGNORE INTO daily_prices SELECT * FROM temp_df")
            con.unregister('temp_df')

        await context.close()
        await browser.close()
        
    final_count = con.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
    final_stocks = con.execute("SELECT COUNT(DISTINCT stock_id) FROM daily_prices").fetchone()[0]
    print(f"✨ Playwright Goodinfo extraction inserted {final_count} local cached DuckDB bounds for {final_stocks} stocks!")
    con.close()

if __name__ == "__main__":
    asyncio.run(main())
