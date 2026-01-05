import pandas as pd
import os
import sys

# Paths
ref_path = "project_tw/references/stock_list_s2006e2025_filtered.xlsx"
out_path = "project_tw/output/stock_list_s2006e2025_filtered.xlsx"

# Check existence
if not os.path.exists(ref_path):
    # Try alternate location
    ref_path = "references/stock_list_s2006e2025_filtered.xlsx"
    
if not os.path.exists(out_path):
    print(f"Output file not found: {out_path}")
    print("Has the analysis finished?")
    sys.exit(1)

if not os.path.exists(ref_path):
    print(f"Reference file not found: {ref_path}")
    sys.exit(1)
    
print(f"Comparing Output:\n  {out_path}\nvs Reference:\n  {ref_path}\n")

# Load
try:
    df_out = pd.read_excel(out_path)
    df_ref = pd.read_excel(ref_path)
except Exception as e:
    print(f"Error reading Excel files: {e}")
    sys.exit(1)

# 1. Column Match
cols_out = list(df_out.columns)
cols_ref = list(df_ref.columns)

print(f"Output Cols: {len(cols_out)}")
print(f"Ref Cols:    {len(cols_ref)}")

missing_in_out = [c for c in cols_ref if c not in cols_out]
extra_in_out = [c for c in cols_out if c not in cols_ref]

if missing_in_out:
    print("\n[FAIL] Missing Columns in Output:")
    print(missing_in_out)
else:
    print("\n[PASS] All Reference Columns Present.")
    
if extra_in_out:
    print("\n[INFO] Extra Columns in Output (New Features?):")
    print(extra_in_out)

# 2. Content Check (First 5 rows)
print("\nTop 5 Output Rows:")
print(df_out.head(5)[['id', 'name', 'id_name_yrs']].to_string())

# 3. Specific ID Check (e.g. 2330)
id_check = "2330" 
print(f"\nChecking {id_check}...")
row_out = df_out[df_out['id'].astype(str) == id_check]
row_ref = df_ref[df_ref['id'].astype(str) == id_check]

if not row_out.empty and not row_ref.empty:
    print("Output Row:")
    print(row_out.iloc[0].to_string())
    print("\nRef Row:")
    print(row_ref.iloc[0].to_string())
else:
    print(f"ID {id_check} not found in one of the files.")
