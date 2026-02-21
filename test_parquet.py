import duckdb
conn = duckdb.connect()
print(conn.execute("DESCRIBE SELECT * FROM read_parquet('data/backup/prices_2004.parquet')").fetchall())
