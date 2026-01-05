import pandas as pd
import os

STOCK_LIST_PATH = 'project_tw/stock_list.csv'
FILTERED_PATH = 'project_tw/output/stock_list_s2006e2025_filtered.xlsx'
UNFILTERED_PATH = 'project_tw/output/stock_list_s2006e2025_unfiltered.xlsx'

KNOWN_NAMES = {
    '5274': '信驊',
    '6640': '均華',
    '00909': '國泰數位支付服務'
}

def patch_specific():
    # 1. Update CSV
    if os.path.exists(STOCK_LIST_PATH):
        df_csv = pd.read_csv(STOCK_LIST_PATH)
        df_csv['code'] = df_csv['code'].astype(str)
        # Upsert
        for k, v in KNOWN_NAMES.items():
            if k in df_csv['code'].values:
                df_csv.loc[df_csv['code'] == k, 'name'] = v
            else:
                new_row = pd.DataFrame([{'code': k, 'name': v}])
                df_csv = pd.concat([df_csv, new_row], ignore_index=True)
        df_csv.to_csv(STOCK_LIST_PATH, index=False)
        print("Updated stock_list.csv")
    
    name_map = KNOWN_NAMES # Or load full? Let's just use KNOWN to force patch.
    
    # 2. Patch Excels
    for p in [UNFILTERED_PATH, FILTERED_PATH]:
        if os.path.exists(p):
            print(f"Patching {p} with specific names...")
            df = pd.read_excel(p)
            df['id'] = df['id'].astype(str)
            
            def fix_name(row):
                code = str(row['id'])
                if code in KNOWN_NAMES:
                    return KNOWN_NAMES[code]
                return row['name']
            
            df['name'] = df.apply(fix_name, axis=1)
            
            # Fix id_name_yrs
            def fix_id_name_yrs(row):
                try:
                    parts = str(row['id_name_yrs']).split('_')
                    if len(parts) >= 3:
                        code = parts[0] # Assuming first is ID
                        if code in KNOWN_NAMES:
                             parts[1] = KNOWN_NAMES[code]
                             return "_".join(parts)
                except:
                    pass
                return row['id_name_yrs']
                
            df['id_name_yrs'] = df.apply(fix_id_name_yrs, axis=1)
            
            df.to_excel(p, index=False)
            print("  Saved.")

if __name__ == "__main__":
    patch_specific()
