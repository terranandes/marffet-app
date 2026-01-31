import requests
import pandas as pd
import io

def probe(mode):
    url = f"https://isin.twse.com.tw/isin/C_public.jsp?strMode={mode}"
    print(f"Probing Mode {mode}...")
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        resp.encoding = 'big5'
        dfs = pd.read_html(io.StringIO(resp.text), header=0)
        if dfs:
            print(f"✅ Mode {mode} Content:")
            print(dfs[0].head(20)) # Print first 20 rows
        else:
            print(f"❌ Mode {mode} parsed but no text")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Common guesses for Bonds/CBs
    probe(1) # Maybe "All"?
    probe(3) # Often Listed Bonds
    probe(5) # Often OTC Bonds
    probe(6) # Often Emerging?
