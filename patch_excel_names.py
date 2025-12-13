import pandas as pd
import yfinance as yf
import httpx
import asyncio
import os

STOCK_LIST_PATH = 'project_tw/stock_list.csv'
FILTERED_PATH = 'project_tw/output/stock_list_s2006e2025_filtered.xlsx'
UNFILTERED_PATH = 'project_tw/output/stock_list_s2006e2025_unfiltered.xlsx'

async def fetch_missing_names(codes):
    """Try to fetch missing names via YFinance or Snippet"""
    new_names = {}
    
    # 1. Try YFinance (Batch?)
    print(f"Fetching names for {len(codes)} stocks via YFinance...")
    for code in codes:
        try:
            # Try .TWO then .TW
            suffixes = ['.TWO', '.TW']
            found_name = None
            for s in suffixes:
                ticker = yf.Ticker(f"{code}{s}")
                try:
                    # info might fetch slowly
                    # Fast fetch?
                    # t.history(period='1d') check empty?
                    # info key 'longName'
                    info = ticker.info
                    name = info.get('longName') or info.get('shortName')
                    if name:
                        # If English, maybe useful? Prefer Chinese.
                        # YF often returns English for TW stocks if locale not set?
                        # Actually YF returns mixed.
                        # We can try to guess Chinese from 'symbol' if returned?
                        # Let's just use what we get, better than "Unknown"
                        found_name = name
                        break
                except:
                    pass
            
            if found_name:
                print(f"  Found {code}: {found_name}")
                new_names[code] = found_name
            else:
                print(f"  Failed to find name for {code}")
        except Exception as e:
            print(f"Error {code}: {e}")

    return new_names

def patch_file(path, name_map):
    print(f"Patching {path}...")
    if not os.path.exists(path):
        print(f"  {path} not found.")
        return

    df = pd.read_excel(path)
    df['id'] = df['id'].astype(str)
    
    # 1. Remove 'L' stocks
    # "Filter out ETFs with postfix 'L'"
    # Check ID column
    original_len = len(df)
    df = df[~df['id'].str.endswith('L')]
    filtered_len = len(df)
    if original_len != filtered_len:
        print(f"  Removed {original_len - filtered_len} leveraged (L) stocks.")
    
    # 2. Fix Names
    # If name is 'Unknown', 'nan', or SAME AS CODE, try map
    def fix_name(row):
        code = str(row['id'])
        current_name = str(row['name'])
        
        # Conditions to overwrite:
        # 1. Unknown
        # 2. nan
        # 3. code == name (e.g. "6498" == "6498")
        if current_name == 'Unknown' or current_name == 'nan' or current_name == code:
            mapped = name_map.get(code)
            if mapped: 
                return mapped
            return 'Unknown' # If missing in map, set to Unknown (or keep code?)
            # User wants formal name. If map misses, 'Unknown' is honest.
            # But let's keep Code if Map misses, as fallback?
            # User complained about "Unknown". Code is better than "Unknown".
            # User said "please get the name formally".
            # For now, if missing in map, return Code.
            # But wait, verify output showed "6498: 6498". 
            # I want to overwrite logic if map HAS it.
            
        return current_name

    df['name'] = df.apply(fix_name, axis=1)
    
    # Update id_name_yrs
    # id_name_yrs format: "6640_Unknown_9" -> "6640_Name_9"
    def fix_id_name_yrs(row):
        try:
            parts = str(row['id_name_yrs']).split('_')
            # Assuming id_name_yrs is ID_NAME_YRS
            if len(parts) >= 3:
                parts[1] = str(row['name'])
                return "_".join(parts)
        except:
            pass
        return row['id_name_yrs']

    df['id_name_yrs'] = df.apply(fix_id_name_yrs, axis=1)
    
    # Save
    df.to_excel(path, index=False)
    print("  Saved.")
    
    # Return missing
    missing = df[df['name'] == 'Unknown']['id'].unique().tolist()
    return missing

async def main():
    # Load Name Map
    name_map = {}
    if os.path.exists(STOCK_LIST_PATH):
        df = pd.read_csv(STOCK_LIST_PATH)
        df['code'] = df['code'].astype(str)
        name_map = dict(zip(df['code'], df['name']))
    
    # Patch Files
    missing_unf = patch_file(UNFILTERED_PATH, name_map)
    patch_file(FILTERED_PATH, name_map) # Filtered is subset
    
    if missing_unf:
        print(f"Still missing {len(missing_unf)} names (e.g., {missing_unf[:5]}). Fetching...")
        new_names = await fetch_missing_names(missing_unf)
        
        if new_names:
            # Update Map
            name_map.update(new_names)
            # Append to CSV
            new_rows = [{'code': k, 'name': v} for k, v in new_names.items()]
            current_df = pd.read_csv(STOCK_LIST_PATH) if os.path.exists(STOCK_LIST_PATH) else pd.DataFrame(columns=['code', 'name'])
            # Merge
            updated_df = pd.concat([current_df, pd.DataFrame(new_rows)]).drop_duplicates(subset='code', keep='last')
            updated_df.to_csv(STOCK_LIST_PATH, index=False)
            print("Updated stock_list.csv")
            
            # Repatch
            patch_file(UNFILTERED_PATH, name_map)
            patch_file(FILTERED_PATH, name_map)

if __name__ == "__main__":
    asyncio.run(main())
