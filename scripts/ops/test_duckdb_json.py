import duckdb
import time
from pathlib import Path

def test_json_read():
    conn = duckdb.connect(':memory:')
    json_path = 'data/raw/Market_2000_Prices.json'
    if not Path(json_path).exists():
        print(f"File {json_path} not found")
        return

    start = time.time()
    try:
        # Try to read using read_blob and json_each
        print("Testing native JSON read via read_blob...")
        res = conn.execute(f"""
            SELECT 
                key, 
                unnest(value.daily).d as date,
                unnest(value.daily).c as close
            FROM json_each((SELECT CAST(read_blob('{json_path}') AS JSON)))
            LIMIT 10
        """).fetchall()
        for r in res:
            print(r)
        
        duration = time.time() - start
        print(f"Native read (10 rows) took {duration:.4f}s")
        
        # Now try a full count to see performance
        start = time.time()
        count = conn.execute(f"""
            SELECT count(*)
            FROM (
                SELECT unnest(value.daily)
                FROM json_each((SELECT CAST(read_blob('{json_path}') AS JSON)))
            )
        """).fetchone()[0]
        duration = time.time() - start
        print(f"Full unnest count ({count} rows) took {duration:.4f}s")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_json_read()
