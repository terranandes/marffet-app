
import json
import math
from pathlib import Path

def check_all_integrity():
    data_dir = Path("data/raw")
    corrupted = []
    
    for year in range(2000, 2027):
        # Check Prices
        for prefix in ["", "TPEx_"]:
            fpath = data_dir / f"{prefix}Market_{year}_Prices.json"
            if fpath.exists():
                try:
                    with open(fpath, 'r') as f:
                        json.load(f)
                except Exception as e:
                    print(f"❌ Corrupted: {fpath.name} - {type(e).__name__}")
                    corrupted.append(fpath)
        
        # Check Dividends
        div_path = data_dir / f"TWSE_Dividends_{year}.json"
        if div_path.exists():
            try:
                with open(div_path, 'r') as f:
                    json.load(f)
            except Exception as e:
                print(f"❌ Corrupted: {div_path.name} - {type(e).__name__}")
                corrupted.append(div_path)

    if not corrupted:
        print("✅ All local JSON files are healthy.")
    else:
        print(f"⚠️ Found {len(corrupted)} corrupted files.")
    return corrupted

if __name__ == "__main__":
    check_all_integrity()
