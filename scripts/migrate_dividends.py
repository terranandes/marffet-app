"""
Script to migrate legacy dividend data (dividends_all.json) 
into modern hybrid cache (app/data/dividends/*.json).

Logic:
1. Iterate through all stock IDs in data/dividends_all.json
2. Check if app/data/dividends/{id}.json exists
3. If not, create it.
4. If exists, merge missing years.
   - Legacy data is {"year": {"cash": X, "stock_split": Y}}
   - Modern data is [{"date": "YYYY-MM-DD", "amount": X}]
   - Since legacy lacks full date, we use "YYYY-01-01" as placeholder if missing.
"""

import json
import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
LEGACY_FILE = BASE_DIR / "data" / "dividends_all.json"
CACHE_DIR = BASE_DIR / "app" / "data" / "dividends"

def main():
    if not LEGACY_FILE.exists():
        print(f"Legacy file not found: {LEGACY_FILE}")
        return

    print(f"Loading legacy data from {LEGACY_FILE}...")
    with open(LEGACY_FILE, "r") as f:
        legacy_data = json.load(f)

    if not CACHE_DIR.exists():
        os.makedirs(CACHE_DIR)

    migrated_count = 0
    merged_count = 0
    unique_years_added = 0

    for stock_id, years_data in legacy_data.items():
        # Normalize ID (e.g. remove suffixes if any in legacy? Legacy uses pure ID mostly)
        clean_id = str(stock_id).strip()
        modern_file = CACHE_DIR / f"{clean_id}.json"
        
        modern_data = {
            "stock_id": clean_id,
            "stock_name": "", # Unknown from legacy file
            "last_synced": datetime.now().isoformat(),
            "source": "legacy_migration",
            "dividends": []
        }
        
        # Load existing if present
        if modern_file.exists():
            try:
                with open(modern_file, "r") as f:
                    modern_data = json.load(f)
            except Exception as e:
                print(f"Error loading {modern_file}: {e}")
                continue

        # Create lookup of existing years in modern data
        existing_years = set()
        for d in modern_data.get("dividends", []):
            try:
                y = d["date"].split("-")[0]
                existing_years.add(y)
            except: pass

        # Merge
        changed = False
        sorted_years = sorted(years_data.keys(), key=lambda x: int(x), reverse=True)
        
        for year_str in sorted_years:
            if year_str not in existing_years:
                entry = years_data[year_str]
                cash = entry.get("cash", 0.0)
                
                # Only migrate if cash > 0 (as modern cache is cash-focused for now)
                # Stock dividends are complex to map to "amount" without confusion.
                # Assuming "amount" = cash dividend.
                if cash > 0:
                    new_entry = {
                        "date": f"{year_str}-01-01", # Placeholder
                        "amount": cash,
                         # Add note? No standard field for source.
                    }
                    modern_data["dividends"].append(new_entry)
                    existing_years.add(year_str)
                    unique_years_added += 1
                    changed = True

        if changed:
            # Sort by date desc
            modern_data["dividends"].sort(key=lambda x: x["date"], reverse=True)
            
            with open(modern_file, "w") as f:
                json.dump(modern_data, f, indent=2, ensure_ascii=False)
            
            if modern_file.exists():
                merged_count += 1
            else:
                migrated_count += 1
                
    print(f"Migration Complete.")
    print(f"Total Stocks Processed: {len(legacy_data)}")
    print(f"Stocks Updated/Created: {merged_count + migrated_count}")
    print(f"Total Unique Years Added: {unique_years_added}")

if __name__ == "__main__":
    main()
