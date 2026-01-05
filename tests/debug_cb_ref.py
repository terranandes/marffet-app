
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
