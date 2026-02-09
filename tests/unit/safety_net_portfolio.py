
import unittest
import sqlite3
import os
import shutil
from pathlib import Path
from datetime import datetime

# Import the module under test
# We will test the functions directly before and after refactor
# Import the module under test
# We will test the functions directly before and after refactor
from app import database
from app.services import portfolio_service, calculation_service
from app.repositories import group_repo

class TestPortfolioDBSafetyNet(unittest.TestCase):
    def setUp(self):
        # Use a temporary DB for testing
        self.test_db_path = Path("test_portfolio_safety.db")
        
        # Monkeypatch the DB_PATH in the module
        database.DB_PATH = self.test_db_path
        
        # Initialize DB
        if self.test_db_path.exists():
            os.remove(self.test_db_path)
            
        database.init_db()
        self.user_id = "test_user_safety_net"

    def tearDown(self):
        if self.test_db_path.exists():
            os.remove(self.test_db_path)

    def test_full_lifecycle(self):
        """
        Test the full lifecycle of a portfolio:
        1. Create Group
        2. Add Target
        3. Add Transactions (Buy/Sell)
        4. Verify Calculations (Avg Cost, P&L)
        5. Delete
        """
        print("\n[SafetyNet] Starting Full Lifecycle Test...")

        # 1. Create Group
        group = portfolio_service.create_group(self.user_id, "My Safety Group")
        self.assertIsNotNone(group['id'])
        self.assertEqual(group['name'], "My Safety Group")
        print("[SafetyNet] Group Created")

        # 2. Add Target
        # Use a real stock ID but mock name fetch (or let it fail gracefully)
        target = portfolio_service.add_target(group_id=group['id'], stock_id="2330", stock_name="TSMC", asset_type="stock")
        self.assertEqual(target['stock_id'], "2330")
        self.assertEqual(target['stock_name'], "TSMC")
        print("[SafetyNet] Target Added")

        # 3. Add Transactions
        # Buy 1000 shares @ 500
        # tx_date format: YYYY-MM-DD
        portfolio_service.add_transaction(target_id=target['id'], tx_type="buy", shares=1000, price=500.0, tx_date="2023-01-01")
        # Buy 1000 shares @ 600
        portfolio_service.add_transaction(target_id=target['id'], tx_type="buy", shares=1000, price=600.0, tx_date="2023-02-01")
        # Sell 500 shares @ 700
        portfolio_service.add_transaction(target_id=target['id'], tx_type="sell", shares=500, price=700.0, tx_date="2023-03-01")
        print("[SafetyNet] Transactions Added")

        # 4. Verify Summary Logic (Crucial!)
        # Total Bought: 2000 shares, Cost: 500k + 600k = 1.1M. Avg Cost: 550.
        # Sold 500 @ 700. 
        # Avg Cost of Sold Shares = 550 * 500 = 275,000.
        # Realized PnL: (700 * 500) - 275,000 = 350,000 - 275,000 = 75,000.
        # Remaining: 1500 shares. 
        # Remaining Total Cost (Internal Logic): total_cost = max(0, total_shares * avg_cost_per_share)
        # = 1500 * 550 = 825,000.
        
        # Test Case assumptions:
        current_price = 800.0
        summary = calculation_service.get_target_summary(target['id'], current_price=current_price)
        
        # Verify Shares
        self.assertEqual(summary['total_shares'], 1500, "Remaining shares should be 1500")
        
        # Verify Avg Cost (Allow small float error)
        self.assertAlmostEqual(summary['avg_cost'], 550.0, places=2, msg="Avg cost should be 550")
        
        # Verify Total Cost
        self.assertAlmostEqual(summary['total_cost'], 825000.0, places=2, msg="Total cost should be 825k")
        
        # Verify Realized PnL
        self.assertAlmostEqual(summary.get('realized_pnl', 0), 75000.0, places=2, msg="Realized PnL should be 75k")
        
        # Verify Unrealized PnL (at price 800)
        # Market Value = 1500 * 800 = 1,200,000.
        # Cost Basis = 825,000.
        # Unrealized PnL = 375,000.
        expected_unrealized = (1500 * current_price) - 825000
        self.assertAlmostEqual(summary.get('unrealized_pnl', 0), expected_unrealized, places=2)
        
        print("[SafetyNet] Calculations Verified")

        # 5. List Groups check
        groups = portfolio_service.list_groups(self.user_id)
        # We created 1 group. But if create_group initializes default portfolio (3 groups), then we might have 4.
        # Let's check if our group is in the list by ID.
        group_ids = [g['id'] for g in groups]
        self.assertIn(group['id'], group_ids)
        
        # 6. Delete
        portfolio_service.delete_group(group['id'])
        groups_after = portfolio_service.list_groups(self.user_id)
        # Should be empty or at least not contain the deleted one
        guids = [g['id'] for g in groups_after]
        self.assertNotIn(group['id'], guids)
        print("[SafetyNet] Deletion Verified")

if __name__ == '__main__':
    unittest.main()
