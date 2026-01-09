
import pandas as pd
import json
import os
import sys

# Paths
GOLDEN_EXCEL = "references/stock_list_s2006e2025_filtered.xlsx"
DATA_DIR = "data/raw"

def verify_targets():
    print(f"🔍 Loading Golden Excel: {GOLDEN_EXCEL}...")
    try:
        df = pd.read_excel(GOLDEN_EXCEL)
    except Exception as e:
        print(f"❌ Failed to load Excel: {e}")
        return

    print(f"✅ Loaded {len(df)} targets.")
    
    # Load Price Data Cache
    prices_db = {}
    print("   Loading Price Data (2006-2025)...")
    for year in range(2006, 2026):
        p_file = os.path.join(DATA_DIR, f"Market_{year}_Prices.json")
        if os.path.exists(p_file):
            with open(p_file, 'r') as f:
                prices_db[year] = json.load(f)
        else:
            prices_db[year] = {}
            
        # Load TPEx
        t_file = os.path.join(DATA_DIR, f"TPEx_Market_{year}_Prices.json")
        if os.path.exists(t_file):
             with open(t_file, 'r') as f:
                prices_db[year].update(json.load(f))

    issues = []
    
    print("\n🚀 Starting Correlation...")
    for index, row in df.iterrows():
        stock_id = str(row['id'])
        name = row['name']
        
        # Check Price Availability
        years_with_data = 0
        first_year = None
        last_year = None
        
        for year in range(2006, 2026):
            p_data = prices_db.get(year, {}).get(stock_id)            
            if p_data:
                years_with_data += 1
                if first_year is None: first_year = year
                last_year = year
        
        status = "✅ OK"
        details = f"{years_with_data} yrs ({first_year}-{last_year})"
        
        if years_with_data == 0:
            status = "❌ NO DATA"
            issues.append({'id': stock_id, 'name': name, 'error': 'No Price Data found in JSONs'})
        elif years_with_data < 5:
             status = "⚠️ LOW DATA"
             issues.append({'id': stock_id, 'name': name, 'error': f'Only {years_with_data} years of data'})

        print(f"[{index+1}/{len(df)}] {stock_id} {name}: {status} - {details}")

    print("\n" + "="*30)
    print(f"🏁 Verification Complete. Found {len(issues)} issues.")
    if issues:
        print("Issues found:")
        for i in issues:
            print(f" - {i['id']} {i['name']}: {i['error']}")
    else:
        print("✅ All targets have corresponding price data.")

if __name__ == "__main__":
    verify_targets()
