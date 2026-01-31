import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


import pandas as pd
import os

path = 'references/CB6533.xlsx'
if os.path.exists(path):
    try:
        df = pd.read_excel(path)
        print("COLUMNS:", df.columns.tolist())
        print("HEAD (2 rows):")
        print(df.head(2).to_string())
    except Exception as e:
        print("Error reading:", e)
else:
    print("File not found.")
