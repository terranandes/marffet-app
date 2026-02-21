import pandas as pd
import requests
import os
import io

class StockInfoService:
    @staticmethod
    def _fetch_html_text(url: str) -> str:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            # TWSE is usually Big5. Requests might auto-detect ISO-8859-1.
            # Force encoding if we know it, or let it guess from charset in meta.
            # Using 'big5' is standard for older TW sites.
            resp.encoding = 'big5' 
            return resp.text
        except Exception as e:
            print(f"[StockInfo] HTTP Error {url}: {e}")
            return None

    @staticmethod
    def fetch_stock_list() -> pd.DataFrame:
        """
        Fetch stock list from TWSE ISIN page (O(1) request).
        Returns DataFrame with columns: [code, name, type, industry]
        """
        print("[StockInfo] Fetching official lists from TWSE/TPEX...")
        
        # URL for Listed (Mode=2) and OTC (Mode=4)
        # MUST use HTTPS to avoid redirect to Port 8443 (which is often blocked)
        url_listed = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
        url_otc = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4"
        url_bonds = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=3"
        
        dfs = []
        try:
            # 1. Fetch Listed
            print(f"[StockInfo] Requesting {url_listed}...")
            html_listed = StockInfoService._fetch_html_text(url_listed)
            if html_listed:
                # Wrap in StringIO to ensure pandas treats it as content, not filename
                listed_dfs = pd.read_html(io.StringIO(html_listed), header=0)
                if listed_dfs:
                    df_listed = listed_dfs[0]
                    df_listed['type'] = 'Listed'
                    dfs.append(df_listed)
                
            # 2. Fetch OTC
            print(f"[StockInfo] Requesting {url_otc}...")
            html_otc = StockInfoService._fetch_html_text(url_otc)
            if html_otc:
                otc_dfs = pd.read_html(io.StringIO(html_otc), header=0)
                if otc_dfs:
                    df_otc = otc_dfs[0]
                    df_otc['type'] = 'OTC'
                    dfs.append(df_otc)

            # 3. Fetch Bonds (Convertible Bonds)
            print(f"[StockInfo] Requesting {url_bonds}...")
            html_bonds = StockInfoService._fetch_html_text(url_bonds)
            if html_bonds:
                bond_dfs = pd.read_html(io.StringIO(html_bonds), header=0)
                if bond_dfs:
                    df_bonds = bond_dfs[0]
                    # Filter: Only keep rows where column 0 has 2 parts (Code Name)
                    # This implicitly filters out the subheaders like "轉換公司債"
                    df_bonds['type'] = 'Bond'
                    dfs.append(df_bonds)
                
        except Exception as e:
            print(f"[StockInfo] Error processing HTML: {e}")
            return pd.DataFrame()

        if not dfs:
            return pd.DataFrame()
            
        # Merge
        raw_df = pd.concat(dfs, ignore_index=True)
        
        # Clean Data
        # Target Column 0: "有價證券代號及名稱" -> "2330 　台積電"
        # We need to split this.
        
        data = []
        # Identify the correct column index. usually 0.
        # Let's verify column names if possible, but they might be Chinese.
        # We assume column 0 is the code/name composite.
        
        col_0 = raw_df.columns[0]
        col_industry = raw_df.columns[4] if len(raw_df.columns) > 4 else None
        
        for _, row in raw_df.iterrows():
            try:
                val = str(row[col_0])
                # Split by space
                parts = val.split(None, 1) # Split on first whitespace
                if len(parts) == 2:
                    code, name = parts
                    # Filter: Maintain only Stock/ETF codes?
                    # Generally Stocks are 4 digits, ETFs 5 digits or start with 00...
                    # We keep ALL for now, consumer filters later.
                    
                    industry = str(row[col_industry]) if col_industry else ""
                    
                    data.append({
                        "code": code.strip(),
                        "name": name.strip(),
                        "industry": industry,
                        "market_type": row['type']
                    })
            except Exception:
                continue
                
        return pd.DataFrame(data)

    @staticmethod
    def update_cache(output_path="app/project_tw/stock_list.csv"):
        """
        Fetch and save to CSV.
        """
        df = StockInfoService.fetch_stock_list()
        if not df.empty:
            # Ensure dir exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"[StockInfo] Saved {len(df)} stocks to {output_path}")
            return True
        else:
            print("[StockInfo] Failed to fetch data.")
            return False
