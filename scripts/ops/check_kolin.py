import duckdb
con = duckdb.connect('data/market.duckdb', read_only=True)
print('1606 Kolin End of Life Prices:')
print(con.execute("SELECT date, close FROM daily_prices WHERE stock_id='1606' ORDER BY date DESC LIMIT 10").df())
con.close()
