
import pandas as pd
import json
import os
from pathlib import Path

# Paths
BASE_DIR = Path("/home/terwu01/github/martian")
EXCEL_PATH = BASE_DIR / "app/project_tw/references/stock_list_s2006e2026_filtered.xlsx"
DATA_DIR = BASE_DIR / "data/raw"

# Refactored for Clean Room Correlation
# Expected: From Excel (Unfiltered) - Reference Only
# Actual: From Data Lake (Scraped via ISIN)

EXCEL_PATH = BASE_DIR / "app/project_tw/references/stock_list_s2006e2026_unfiltered.xlsx"

def load_excel_stocks():
    print(f"Loading Reference Excel: {EXCEL_PATH}")
    try:
        df = pd.read_excel(EXCEL_PATH, dtype=str)
        # return Set of IDs
        return set(df.iloc[:, 0].str.strip())
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return set()

def scan_data_lake():
    covered_stocks = set()
    # Check 2006 and 2026 as proxies for full coverage
    # Data is cumulative in this new scraper? No, yearly files.
    # But ISIN scraper runs for 2006-2026 range.
    years = range(2006, 2027)
    
    for year in years:
        fpath = DATA_DIR / f"Market_{year}_Prices.json"
        if fpath.exists():
            try:
                with open(fpath, 'r') as f:
                    data = json.load(f)
                    covered_stocks.update(data.keys())
            except:
                pass
    return covered_stocks

def main():
    reference_stocks = load_excel_stocks()
    scraped_stocks = scan_data_lake()
    
    print(f"Reference Stocks (Excel): {len(reference_stocks)}")
    print(f"Scraped Stocks (ISIN/Clean): {len(scraped_stocks)}")
    
    missing_from_scrape = reference_stocks - scraped_stocks
    new_in_scrape = scraped_stocks - reference_stocks
    
    print(f"Missing from Scrape (vs Excel): {len(missing_from_scrape)}")
    if missing_from_scrape:
        print(f"Sample Missing: {list(missing_from_scrape)[:10]}")
        # Analysis: These are likely delisted stocks not in ISIN now.
        
    print(f"New in Scrape (Not in Excel): {len(new_in_scrape)}")
    if new_in_scrape:
        print(f"Sample New: {list(new_in_scrape)[:10]}")

    common = reference_stocks.intersection(scraped_stocks)
    print(f"Common/Correlated: {len(common)}")

if __name__ == "__main__":
    main()
