import logging
logging.basicConfig(level=logging.INFO)

from app.services.market_db import _resolve_db_path, get_connection
import os
import shutil

# Remove DB to force rehydrate again
db_path = _resolve_db_path()
print("Resolved DB path:", db_path)
if db_path.exists():
    os.remove(str(db_path))

# Force re-evaluation by calling it directly
from app.services.market_db import _rehydrate_from_parquet
_rehydrate_from_parquet(db_path)

conn = get_connection()
try:
    count = conn.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
    print(f"Rehydrated! DB has {count} rows in daily_prices.")
finally:
    conn.close()
