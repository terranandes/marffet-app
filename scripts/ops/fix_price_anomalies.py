import json
import os
import sys

# Ensure we can import app
sys.path.append(os.getcwd())

from app.services.market_db import get_connection

def fix_anomalies():
    ANOMALY_FILE = 'tests/performance/price_anomalies.json'
    if not os.path.exists(ANOMALY_FILE):
        print(f"❌ {ANOMALY_FILE} not found.")
        return
        
    with open(ANOMALY_FILE, 'r') as f:
        anomalies = json.load(f)
        
    print(f"🛠️ Fixing {len(anomalies)} price anomalies in DuckDB...")
    
    conn = get_connection(read_only=False)
    try:
        deleted_count = 0
        for a in anomalies:
            sid = a['stock_id']
            date_str = a['date'][:10] # YYYY-MM-DD
            
            # Delete the specific erroneous row
            conn.execute("DELETE FROM daily_prices WHERE stock_id = ? AND date = ?", [sid, date_str])
            deleted_count += 1
            
        print(f"✅ Deleted {len(anomalies)} rows.")
        
        # Verify 1752 specifically
        res = conn.execute("SELECT COUNT(*) FROM daily_prices WHERE stock_id = '1752' AND date = '2025-01-10'").fetchone()
        print(f"Confirm 1752 deletion: {res[0]} rows remaining on 2025-01-10.")
        
    except Exception as e:
        print(f"❌ Error fixing anomalies: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_anomalies()
