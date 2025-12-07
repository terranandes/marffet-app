
import httpx
import asyncio
import json
import os
import time
import pandas as pd
from datetime import datetime, timedelta

class TWSECrawler:
    def __init__(self, data_dir="data/raw"):
        self.base_url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        # TWSE has strict rate limits (suggestion: 3s delay)
        self.rate_limit_delay = 1.5 

    def _taiwan_to_ad(self, date_str):
        """Convert '113/01/02' to '2024-01-02'"""
        try:
            parts = date_str.split('/')
            year = int(parts[0]) + 1911
            return f"{year}-{parts[1]}-{parts[2]}"
        except Exception:
            return None

    async def fetch_stock_month(self, stock_code: str, date_str: str):
        """
        Fetch data for a specific month. 
        date_str format: 'YYYYMM01' (e.g. '20240101')
        """
        file_path = os.path.join(self.data_dir, f"{stock_code}_{date_str}.json")
        
        # Check Cache
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        params = {
            "response": "json",
            "date": date_str,
            "stockNo": stock_code
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        async with httpx.AsyncClient() as client:
            print(f"Fetching {stock_code} for {date_str}...")
            try:
                resp = await client.get(self.base_url, params=params, headers=headers, timeout=10.0)
                resp.raise_for_status()
                data = resp.json()
                
                # Basic validation
                if data.get('stat') == 'OK':
                    # Normalize columns if needed, but saving raw is safer first
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False)
                    return data
                else:
                    return None
            except Exception as e:
                print(f"Error fetching {stock_code} {date_str}: {e}")
                return None
            finally:
                # Naive rate limit wait
                await asyncio.sleep(self.rate_limit_delay)

    async def fetch_history(self, stock_code: str, start_year: int, end_year: int):
        """Fetch range of history. Logic needed to iterate months."""
        results = []
        current_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y%m01")
            
            # Skip future dates
            if current_date > datetime.now():
                break

            data = await self.fetch_stock_month(stock_code, date_str)
            if data and data.get('stat') == 'OK':
                results.append(data)
            
            # Next month
            # Calculate next month safely
            next_month = current_date.month + 1
            next_year = current_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            current_date = datetime(next_year, next_month, 1)
            
        return results

    def parse_to_dataframe(self, raw_data_list):
        """Convert list of TWSE JSON responses to a single Pandas DataFrame"""
        all_rows = []
        for data in raw_data_list:
            if not data or data.get('stat') != 'OK':
                continue
            
            # Fields: ["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交筆數"]
            # English map for internal use
            for row in data['data']:
                # Clean numeric strings (remove commas)
                cleaned_row = {
                    'date': self._taiwan_to_ad(row[0]),
                    'volume': int(row[1].replace(',', '')),
                    'open': float(row[3].replace(',', '').replace('--', '0')) if row[3] != '--' else 0,
                    'high': float(row[4].replace(',', '').replace('--', '0')) if row[4] != '--' else 0,
                    'low': float(row[5].replace(',', '').replace('--', '0')) if row[5] != '--' else 0,
                    'close': float(row[6].replace(',', '').replace('--', '0')) if row[6] != '--' else 0,
                }
                all_rows.append(cleaned_row)
        
        df = pd.DataFrame(all_rows)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)
        return df

# Helper to run async from sync context if needed
def get_stock_history_df(stock_code, start_year, end_year):
    crawler = TWSECrawler()
    raw_list = asyncio.run(crawler.fetch_history(stock_code, start_year, end_year))
    return crawler.parse_to_dataframe(raw_list)
