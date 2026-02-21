import pandas as pd
import duckdb

def analyze_mismatch():
    ref_df = pd.read_excel('app/project_tw/references/stock_list_s2006e2026_unfiltered.xlsx')
    
    con = duckdb.connect('data/market.duckdb')
    my_prices = con.execute("SELECT stock_id, date, close FROM daily_prices WHERE cast(date as varchar) LIKE '2006%'").df()
    
    print("Top 5 Mismatch Examples to find precisely what date Reference used for 2006 Start:")
    # We will pick a few stable stocks like 2330, 2412, 1101
    test_stocks = ['2330', '2412', '1101', '2382']
    
    for code in test_stocks:
        ref_row = ref_df[ref_df['id'] == int(code)]
        if not ref_row.empty:
            ref_cagr = ref_row.iloc[0]['s2006e2026bao']
            print(f"\n{code}: Ref CAGR = {ref_cagr}%")
            
        my_row = my_prices[my_prices['stock_id'] == code].sort_values('date')
        if not my_row.empty:
            print(my_row.head(5))

    con.close()

if __name__ == "__main__":
    analyze_mismatch()
