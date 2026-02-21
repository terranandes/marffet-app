import yfinance as yf
import pandas as pd
import duckdb
import time

def main():
    con = duckdb.connect('data/market.duckdb')
    con.execute("DELETE FROM daily_prices")
    
    # Read the 2030 reference tickers
    ref_df = pd.read_excel('app/project_tw/references/stock_list_s2006e2026_unfiltered.xlsx')
    valid_tickers = ref_df['id'].astype(str).str.zfill(4).tolist()
    
    print(f"🚀 Recovering pure nominal boundaries iteratively for {len(valid_tickers)} references...")
    
    all_records = []
    
    for idx, t in enumerate(valid_tickers):
        print(f"[{idx+1}/{len(valid_tickers)}] Processing {t}...", end='\r')
        
        # Test .TW then .TWO
        df = pd.DataFrame()
        market = 'TWSE'
        for suffix in ['.TW', '.TWO']:
            try:
                # auto_adjust=False gives NOMINAL prices natively
                df = yf.Ticker(f"{t}{suffix}").history(period="max", auto_adjust=False, actions=False)
                if not df.empty and 'Close' in df.columns:
                    market = 'TWSE' if suffix == '.TW' else 'TPEx'
                    break
            except Exception as e:
                pass
        
        # Soft rate limit protection
        time.sleep(0.05)
            
        if df.empty or 'Close' not in df.columns:
            continue
            
        stock_series = df['Close'].dropna()
        if stock_series.empty:
            continue
            
        # Filter from 2006 onward
        stock_series = stock_series[stock_series.index.year >= 2006]
        if stock_series.empty:
            continue
            
        # Group by year to find boundaries
        yearly_groups = stock_series.groupby(stock_series.index.year)
        
        for year, group in yearly_groups:
            if group.empty: continue
            
            start_date = group.index.min()
            start_price = float(group.loc[start_date])
            
            end_date = group.index.max()
            end_price = float(group.loc[end_date])
            
            all_records.append({
                'stock_id': t,
                'date': start_date.strftime('%Y-%m-%d'),
                'open': start_price,
                'high': start_price,
                'low': start_price,
                'close': start_price,
                'volume': 0,
                'market': market
            })
            
            if start_date != end_date:
                all_records.append({
                    'stock_id': t,
                    'date': end_date.strftime('%Y-%m-%d'),
                    'open': end_price,
                    'high': end_price,
                    'low': end_price,
                    'close': end_price,
                    'volume': 0,
                    'market': market
                })
                
        # Flush intermediate to DuckDB every 100 tickers
        if (idx + 1) % 100 == 0 and all_records:
            temp_df = pd.DataFrame(all_records)
            temp_df = temp_df.drop_duplicates(subset=['stock_id', 'date'])
            con.register('temp_df', temp_df)
            con.execute("INSERT OR IGNORE INTO daily_prices SELECT * FROM temp_df")
            con.unregister('temp_df')
            all_records = []

    # Final flush
    if all_records:
        temp_df = pd.DataFrame(all_records)
        temp_df = temp_df.drop_duplicates(subset=['stock_id', 'date'])
        con.register('temp_df', temp_df)
        con.execute("INSERT OR IGNORE INTO daily_prices SELECT * FROM temp_df")
        con.unregister('temp_df')
        
    final_count = con.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
    final_stocks = con.execute("SELECT COUNT(DISTINCT stock_id) FROM daily_prices").fetchone()[0]
    print(f"\n✨ YFinance Nominal Recovery complete! Total DB boundary rows: {final_count} spanning {final_stocks} unique tickers.")
    con.close()

if __name__ == "__main__":
    main()
