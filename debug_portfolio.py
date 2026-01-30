
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.portfolio_db import (
    list_groups, 
    get_all_targets_by_type, 
    get_portfolio_race_data,
    update_price_cache
)

USER_ID = "117319593449969244428" # Dev Admin ID

def test_functions():
    print("[-] Testing list_groups...")
    try:
        groups = list_groups(USER_ID)
        print(f"[OK] Groups: {len(groups)}")
    except Exception as e:
        print(f"[FAIL] list_groups: {e}")
        import traceback
        traceback.print_exc()

    print("\n[-] Testing get_all_targets_by_type...")
    try:
        targets = get_all_targets_by_type(USER_ID)
        print(f"[OK] Targets: {len(targets.get('stock', []))} Stocks, {len(targets.get('cb', []))} CBs")
    except Exception as e:
        print(f"[FAIL] get_all_targets_by_type: {e}")
        import traceback
        traceback.print_exc()

    # This calls update_price_cache internally
    print("\n[-] Testing get_portfolio_race_data (triggers yfinance)...")
    try:
        data = get_portfolio_race_data(USER_ID)
        print(f"[OK] Race Data: {len(data)} points")
        if data:
            print(f"Sample: {data[0]}")
    except Exception as e:
        print(f"[FAIL] get_portfolio_race_data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_functions()
