import httpx
import pandas as pd
import asyncio
import io

async def fetch_isin_names():
    name_map = {}
    
    async with httpx.AsyncClient(verify=False) as client:
        # Mode 2: TWSE (Listed)
        # Mode 4: TPEx (OTC)
        # Mode 5: Emerging (興櫃) - Maybe needed?
        modes = [2, 4, 5] 
        
        for m in modes:
            print(f"Fetching ISIN Mode {m}...")
            try:
                url = f"https://isin.twse.com.tw/isin/C_public.jsp?strMode={m}"
                resp = await client.get(url, timeout=30)
                # Encoding usually Big5 or CP950
                # But requests might auto-detect. Let's force Big5 if needed.
                text = resp.content.decode('big5', errors='ignore')
                
                # Parse with Regex to avoid dependencies
                import re
                # Pattern: Matches "Code Name" in first cell of a row
                # Structure: <tr><td bgcolor="#FFF0D1"><b>1101　台泥</b></td>...
                # Or just <td ...>Code Name</td>
                # Let's search for Code+Space+Name pattern generally.
                # Code: 4-6 chars (alphanumeric). 
                # Space: Fullwidth \u3000 or space.
                # Name: Anything.
                
                # Broad pattern for the specific cell format
                # We iterate over lines to be safer? Or findall.
                
                # Pattern: >(A-Z0-9]{4,6})[ \u3000]+([^<]+)</td>
                # Note: ISIN page usually puts Code+Name in FIRST <td>
                
                matches = re.findall(r'>([A-Z0-9]{4,6})[ \u3000]+([^<]+)</td>', text)
                
                for code, name in matches:
                    code = code.strip()
                    name = name.strip()
                    # Filter?
                    if len(code) >= 4:
                         name_map[code] = name
                         
            except Exception as e:
                print(f"Error Mode {m}: {e}")

    print(f"Collected {len(name_map)} names from ISIN.")
    
    # Save to CSV
    # Merge with existing knwon specific names if any?
    # ISIN is authoritative.
    df = pd.DataFrame(list(name_map.items()), columns=['code', 'name'])
    df.to_csv('project_tw/stock_list.csv', index=False)
    print("Saved to project_tw/stock_list.csv")

if __name__ == "__main__":
    asyncio.run(fetch_isin_names())
