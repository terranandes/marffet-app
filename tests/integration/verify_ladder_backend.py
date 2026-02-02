import sys
import os
import sqlite3
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.portfolio_db import get_leaderboard, init_db, get_db

def seed_test_data():
    """Seed DB with test users for leaderboard"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. User with High ROI but Low Cost (Should be excluded)
        cursor.execute("INSERT OR REPLACE INTO users (id, nickname, total_cost, total_roi, total_wealth) VALUES (?, ?, ?, ?, ?)", 
                       ("test_low_cost", "Low Cost King", 500, 200.0, 1500))
                       
        # 2. User with High ROI and High Cost (Should be #1)
        cursor.execute("INSERT OR REPLACE INTO users (id, nickname, total_cost, total_roi, total_wealth) VALUES (?, ?, ?, ?, ?)", 
                       ("test_high_roi", "ROI King", 10000, 50.0, 15000))
                       
        # 3. User with Medium ROI and High Cost (Should be #2)
        cursor.execute("INSERT OR REPLACE INTO users (id, nickname, total_cost, total_roi, total_wealth) VALUES (?, ?, ?, ?, ?)", 
                       ("test_mid_roi", "Mid ROI", 5000, 10.0, 5500))
                       
        # 4. User with Negative ROI (Should be #3)
        cursor.execute("INSERT OR REPLACE INTO users (id, nickname, total_cost, total_roi, total_wealth) VALUES (?, ?, ?, ?, ?)", 
                       ("test_neg_roi", "Loss Leader", 2000, -10.0, 1800))

        conn.commit()
    print("[Setup] Seeded test data.")

def run_test():
    print("=== Verifying Cash Ladder Backend ===")
    
    # 1. Init DB (ensure tables exist)
    init_db()
    
    # 2. Seed Data
    seed_test_data()
    
    # 3. Fetch Leaderboard
    results = get_leaderboard(limit=10)
    
    print(f"[Result] Got {len(results)} entries in leaderboard.")
    
    # 4. Verify
    # Expectation: 
    # 1. "ROI King" (50.0%)
    # 2. "Mid ROI" (10.0%)
    # 3. "Loss Leader" (-10.0%)
    # "Low Cost King" should be ABSENT (Cost 500 < 1000)
    
    found_ids = [r['id'] for r in results]
    
    if "test_low_cost" in found_ids:
        print("❌ FAILED: 'test_low_cost' should be excluded (Cost < 1000)")
        return
        
    expected_order = ["test_high_roi", "test_mid_roi", "test_neg_roi"]
    # Filter only our test users to check order (ignore existing users in local DB)
    actual_order = [uid for uid in found_ids if uid in expected_order]
    
    if actual_order == expected_order:
        print("✅ SUCCESS: Leaderboard order and filtering correct.")
        for r in results:
            if r['id'] in expected_order:
                print(f"   - {r['nickname']}: ROI {r['roi']}% (Cost ${r['total_cost']})")
    else:
        print(f"❌ FAILED: Order mismatch.\nExpected: {expected_order}\nActual: {actual_order}")

if __name__ == "__main__":
    run_test()
