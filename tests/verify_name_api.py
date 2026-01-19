import sys
from app.portfolio_db import fetch_chinese_name_from_api

def test_api():
    # Test TWSE stock (2330 TSMC)
    print("Testing TWSE (2330)...")
    name_twse = fetch_chinese_name_from_api("2330")
    print(f"2330 -> {name_twse}")
    
    if name_twse != "台積電":
        print(f"⚠️ Warning: 2330 name is '{name_twse}', expected '台積電'. (Might be full company name?)")
    
    # Test TPEx stock (6533 Andes - if it wasn't in cache)
    print("Testing TPEx (6533)...")
    name_tpex = fetch_chinese_name_from_api("6533")
    print(f"6533 -> {name_tpex}")
    
    if "晶心" in str(name_tpex):
        print("✅ TPEx Success")
    else:
        print("❌ TPEx Failed")

if __name__ == "__main__":
    test_api()
