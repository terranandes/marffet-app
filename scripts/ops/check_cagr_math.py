import duckdb
import pandas as pd
from app.project_tw.calculator import ROICalculator

def main():
    con = duckdb.connect('data/market.duckdb', read_only=True)
    df_ref = pd.read_excel('app/project_tw/references/stock_list_s2006e2026_unfiltered.xlsx')
    
    for stock_id in ['2330', '6472', '1262', '1606', '3135']:
        print(f"\\n--- Stock {stock_id} ---")
        try:
            ref_val = df_ref[df_ref['id'] == int(stock_id)]['s2006e2026bao'].values[0]
            print(f"Reference CAGR: {ref_val}%")
        except:
            print("No reference value")
            
        df_prices = con.execute("SELECT date, YEAR(date) as year, open, high, low, close FROM daily_prices WHERE stock_id = ? ORDER BY date", [stock_id]).df()
        if df_prices.empty:
            print("No price data")
            continue
            
        df_prices["date"] = pd.to_datetime(df_prices["date"])
        df_prices = df_prices.set_index("date")
        
        divs = con.execute("SELECT year, cash, stock FROM dividends WHERE stock_id = ?", [stock_id]).fetchall()
        div_dict = {int(r[0]): {"cash": float(r[1] or 0), "stock": float(r[2] or 0)} for r in divs}
        
        calc = ROICalculator()
        res = calc.calculate_complex_simulation(
            df=df_prices,
            start_year=2006,
            principal=1_000_000,
            annual_investment=60_000,
            dividend_data=div_dict,
            stock_code=stock_id
        )
        
        cagr_keys = sorted([k for k in res if k.startswith("s2006e") and k.endswith("bao")])
        if cagr_keys:
            key = 's2006e2026bao' if 's2006e2026bao' in res else cagr_keys[-1]
            print(f"Mars CAGR: {res[key]}% ({key})")
            
        print(f"History snippets:")
        history = res.get('history', [])
        if history:
            print(f"  First: {history[0]}")
            print(f"  Last: {history[-1]}")
            
if __name__ == '__main__':
    main()
