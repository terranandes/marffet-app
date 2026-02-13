import ijson
import sys

def test_ijson(filename):
    print(f"Testing ijson on {filename}...")
    count = 0
    total_daily = 0
    with open(filename, 'rb') as f:
        # Using 'items' instead of 'kvitems' to debug structure if needed
        # But kvitems is what the script uses.
        try:
            for k, v in ijson.kvitems(f, ''):
                count += 1
                if 'daily' in v:
                    total_daily += len(v['daily'])
                if count % 100 == 0:
                    print(f"  Processed {count} stocks...")
        except Exception as e:
            print(f"Error: {e}")
            
    print(f"Total Stocks: {count}")
    print(f"Total Daily Points: {total_daily}")

if __name__ == "__main__":
    test_ijson("data/raw/Market_2010_Prices.json")
