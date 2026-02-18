
import requests
from bs4 import BeautifulSoup
import time

def fetch_mops(co_id, year):
    # MOPS t05st09 (Dividend Policy)
    url = 'https://mops.twse.com.tw/mops/web/t05st09'
    roc_year = year - 1911
    
    # Common headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://mops.twse.com.tw',
        'Referer': 'https://mops.twse.com.tw/mops/web/t05st09'
    }
    
    # Strategies to try
    strategies = [
        # Strategy 1: Standard Search (specific year)
        {
            'encodeURIComponent': '1',
            'step': '1',
            'firstin': '1',
            'off': '1',
            'keyword4': '',
            'code1': '',
            'TYPEK2': '',
            'checkbtn': '',
            'queryName': 'co_id',
            'inpuType': 'co_id',
            'TYPEK': 'all',
            'isnew': 'true',
            'co_id': co_id,
            'year': str(roc_year),
        },
        # Strategy 2: Historical (no year, lists all)
        {
            'encodeURIComponent': '1',
            'step': '1',
            'firstin': '1',
            'off': '1',
            'keyword4': '',
            'code1': '',
            'TYPEK2': '',
            'checkbtn': '',
            'queryName': 'co_id',
            'inpuType': 'co_id',
            'TYPEK': 'all',
            'isnew': 'true',
            'co_id': co_id,
           # 'year': removed
        }
    ]
    
    for i, data in enumerate(strategies):
        print(f"--- Strategy {i+1} ---")
        try:
            r = requests.post(url, data=data, headers=headers, timeout=15)
            r.encoding = 'utf-8' # MOPS is often UTF-8 now but sometimes Big5
            
            print(f"Status: {r.status_code}")
            
            soup = BeautifulSoup(r.text, 'html.parser')
            # Look for specific headers in tables
            tables = soup.find_all('table')
            
            found_data = False
            for tbl in tables:
                txt = tbl.get_text()
                if '現金股利' in txt and '股票股利' in txt:
                    print(f"✅ Found Dividend Table!")
                    found_data = True
                    # Print headers and first data row
                    rows = tbl.find_all('tr')
                    for tr in rows[:5]:
                        cols = [td.get_text(strip=True) for td in tr.find_all(['th', 'td'])]
                        print(cols)
                    break
            
            if found_data:
                return
            else:
                print("❌ No dividend table found.")
                
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(2)

print(f"Fetching 2892 (Year 112/2023) from MOPS...")
fetch_mops('2892', 2023)
