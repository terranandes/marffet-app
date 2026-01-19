
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.project_tw.crawler_cb import CBCrawler

async def verify():
    print("--- Verifying CBCrawler ---")
    crawler = CBCrawler()
    
    # 1. Test Issuance Fetch
    print("1. Fetching Issuance Data...")
    issuance = await crawler.fetch_issuance_data()
    print(f"   Got {len(issuance)} records.")
    
    if issuance:
        print(f"   Sample: {issuance[0]}")
        
        # 2. Test Market Data Fetch (Pick a record)
        # Find one that looks like a valid CB (ShortName has numbers?)
        # Or just use a hardcoded one if we know it.
        # Let's try to parse a code from the first record.
        # ISSBD5 usually has 'BondCode' but user code said it might be tricky.
        # Let's look at the sample keys.
        
        sample = issuance[0]
        bond_code = sample.get('BondCode')
        stock_code = sample.get('StockCode') # Might differ key name
        
        if not bond_code:
            # Try finding one with BondCode
            for r in issuance:
                if r.get('BondCode'):
                    sample = r
                    bond_code = r.get('BondCode')
                    break
        
        print(f"2. Testing Market Data for {bond_code}...")
        if bond_code:
             # Just guess stock code if missing? 'IssuerCode'?
             issuer = sample.get('IssuerCode', '2330') # Default fallback
             
             cb_p, st_p, success = await crawler.get_market_data(bond_code, issuer)
             print(f"   Result: CB={cb_price_fmt(cb_p)}, Stock={cb_price_fmt(st_p)}, Success={success}")
        else:
             print("   Could not find valid BondCode in sample to test YF.")
             
    else:
        print("   ❌ Issuance Data Fetch Failed.")

def cb_price_fmt(p):
    return f"{p:.2f}"

if __name__ == "__main__":
    asyncio.run(verify())
