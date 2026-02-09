import pandas as pd
import os

# Paths
base_dir =  os.getcwd()
ref_path = os.path.join(base_dir, "app/project_tw/references/")
csv_path = os.path.join(base_dir, "app/project_tw/stock_list.csv")
file_unfiltered = os.path.join(ref_path, "stock_list_s2010e2026_unfiltered.xlsx")
file_filtered = os.path.join(ref_path, "stock_list_s2010e2026_filtered.xlsx")

def clean_id(val):
    """Convert value to 4-digit string ID."""
    try:
        # If float (e.g. 50.0), convert to int first
        s = str(int(float(val)))
        # Pad with zeros if needed (e.g. 50 -> 0050)
        return s.zfill(4)
    except:
        return str(val).strip()

def process_correlation():
    print("--- Stock List Correlation & Update (Preserving Metadata) ---")
    
    # 1. Load Existing Metadata (The Source of Truth for Industry/Type)
    print(f"Loading existing metadata from {csv_path}...")
    meta_map = {} # code -> {name, industry, market_type}
    if os.path.exists(csv_path):
        try:
            # Load with string types to preserve "0050"
            df_old = pd.read_csv(csv_path, dtype={'code': str, 'name': str})
            
            # Populate Map
            for _, row in df_old.iterrows():
                code = str(row['code']).strip()
                meta_map[code] = {
                    'name': row['name'], # Keep old name as primary? User said Excel is Golden for *List* but maybe names differ?
                    'industry': row.get('industry', ''),
                    'market_type': row.get('market_type', '')
                }
            print(f"Loaded metadata for {len(meta_map)} stocks.")
        except Exception as e:
            print(f"Warning: Could not load existing CSV: {e}")
            return

    # 2. Load Excel Files (The Source of Truth for *Membership*)
    print("Loading Excel files...")
    df_u = pd.read_excel(file_unfiltered)
    df_f = pd.read_excel(file_filtered)

    # 3. Process & Clean IDs
    df_f['clean_id'] = df_f['id'].apply(clean_id)
    ids_f = set(df_f['clean_id'])

    print(f"Filtered Target Count: {len(ids_f)}")

    # 5. Build New List 
    # Logic: iterate over Filtered IDs. 
    # If exists in Old CSV -> Use Old Metadata (Industry/Type).
    # If New -> Use Empty Metadata (User can fill later or System fetch).
    
    new_rows = []
    seen_ids = set()
    
    # We iterate over df_f to keep order if relevant, or just strictly iterating the set
    # Let's iterate df_f to respect valid rows
    
    for _, row in df_f.iterrows():
        stock_id = clean_id(row['id'])
        excel_name = str(row['name']).strip()
        
        if stock_id in seen_ids:
            continue
        seen_ids.add(stock_id)
        
        # Merge Logic
        meta = meta_map.get(stock_id)
        
        if meta:
            # Exists in old list
            # Prefer Old Name? Or Excel Name?
            # User said "generate golden excel from MoneyCome" -> imply Excel is accurate.
            # But Industry matches Old Name? 
            # Strategy: Use Excel Name (Newest), Old Industry/Type.
            final_name = excel_name if excel_name and excel_name.lower() != 'nan' else meta['name']
            
            new_rows.append({
                "code": stock_id,
                "name": final_name,
                "industry": meta['industry'],
                "market_type": meta['market_type']
            })
        else:
            # New Stock (Not in old list)
            new_rows.append({
                "code": stock_id,
                "name": excel_name,
                "industry": "",
                "market_type": "" 
            })

    # 6. Save Updated CSV
    df_out = pd.DataFrame(new_rows)
    df_out.sort_values(by='code', inplace=True)
    
    df_out.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"\nSUCCESS: Updated {csv_path} with {len(df_out)} stocks.")
    
    # Verification
    print("\n[Sample Rows - Verified Industry]")
    # Check 0050 specifically
    check_ids = ['0050', '1101', '2330']
    print(df_out[df_out['code'].isin(check_ids)].to_string(index=False))

if __name__ == "__main__":
    process_correlation()
