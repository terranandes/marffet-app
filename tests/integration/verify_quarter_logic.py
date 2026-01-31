import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from datetime import datetime
import calendar

def test_quarter_logic():
    # Simulate Date: 2026-01-31 (Current context)
    now = datetime(2026, 1, 31) 
    
    # Logic from `portfolio_db.py`
    quarter_end_month = ((now.month - 1) // 3 + 1) * 3
    last_day = calendar.monthrange(now.year, quarter_end_month)[1]
    end_date = datetime(now.year, quarter_end_month, last_day)
    
    print(f"Current: {now.strftime('%Y-%m-%d')}")
    print(f"Target End Date: {end_date.strftime('%Y-%m-%d')}")
    
    assert end_date.year == 2026
    assert end_date.month == 3
    assert end_date.day == 31
    print("✅ Logic Correct for Jan 2026 -> Mar 2026")

if __name__ == "__main__":
    test_quarter_logic()
