import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import os

ref_path = "project_tw/references/CB6533.xlsx"
if not os.path.exists(ref_path):
    ref_path = "references/CB6533.xlsx"

if os.path.exists(ref_path):
    print(f"Inspecting {ref_path}...")
    try:
        df = pd.read_excel(ref_path)
        print("Columns:", df.columns.tolist())
        print("Shape:", df.shape)
        print("\nFirst 3 rows:")
        print(df.head(3).to_string())
    except Exception as e:
        print(f"Error reading Excel: {e}")
else:
    print(f"File not found: {ref_path}")
