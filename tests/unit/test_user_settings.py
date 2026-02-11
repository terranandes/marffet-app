
import unittest
import sqlite3
from app.repositories import user_repo

class TestUserSettings(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        # Create users table matching schema
        self.conn.execute("""
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                email TEXT,
                name TEXT,
                settings TEXT,
                api_key TEXT,
                last_login_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Insert a user
        self.conn.execute("INSERT INTO users (id, email, name) VALUES ('u1', 'test@example.com', 'Test User')")
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_update_and_get_settings(self):
        # 1. Update settings only
        settings_json = '{"theme": "dark"}'
        success = user_repo.update_user_settings(self.conn, 'u1', settings_json, api_key=None)
        self.assertTrue(success)
        
        # Verify
        data = user_repo.get_user_settings(self.conn, 'u1')
        self.assertEqual(data['settings'], settings_json)
        self.assertIsNone(data['api_key'])
        
        # 2. Update API Key
        success = user_repo.update_user_settings(self.conn, 'u1', settings_json, api_key="secret_key")
        self.assertTrue(success)
        
        data = user_repo.get_user_settings(self.conn, 'u1')
        self.assertEqual(data['api_key'], "secret_key")
        
        # 3. Update settings without changing API Key
        new_settings = '{"theme": "light"}'
        success = user_repo.update_user_settings(self.conn, 'u1', new_settings, api_key=None)
        
        data = user_repo.get_user_settings(self.conn, 'u1')
        self.assertEqual(data['settings'], new_settings)
        self.assertEqual(data['api_key'], "secret_key") # Should remain unchanged

if __name__ == '__main__':
    unittest.main()
