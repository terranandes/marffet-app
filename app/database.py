
import sqlite3
import shutil
from pathlib import Path
from contextlib import contextmanager

# Database file location
# Use persistent storage on Zeabur, fallback to local for dev
# Zeabur mounts volume at /data (as configured in Volumes tab)
# Auto-restore logic: If persistent DB missing, copy from repo (seed/backup)
PERSISTENT_DIR = Path("/data")
REPO_DB_PATH = Path(__file__).parent / "portfolio.db"

if PERSISTENT_DIR.exists() and PERSISTENT_DIR.is_dir():
    DB_PATH = PERSISTENT_DIR / "portfolio.db"
    
    # If persistent DB is missing calling sqlite3.connect would create an empty one.
    # We want to restore from repo backup first if available.
    if not DB_PATH.exists() and REPO_DB_PATH.exists():
        try:
            print(f"[DB] Restoring persistent DB from repo backup: {REPO_DB_PATH}")
            shutil.copy2(REPO_DB_PATH, DB_PATH)
        except Exception as e:
            print(f"[DB] Restore failed: {e}")
            
    print(f"[DB] Using persistent storage: {DB_PATH}")
else:
    DB_PATH = REPO_DB_PATH
    print(f"[DB] Using local storage: {DB_PATH}")

@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    conn.execute("PRAGMA journal_mode=WAL") # Enable Write-Ahead Logging for concurrency
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON") # Enable Cascade Deletes
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialize database with schema."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users (Google Auth)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY, -- Google sub ID
                email TEXT,
                name TEXT,
                nickname TEXT, -- Display Name for Leaderboard
                picture TEXT,
                auth_provider TEXT DEFAULT 'google',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login_at TIMESTAMP
            )
        """)
        
        # Migration: Add nickname if not exists
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN nickname TEXT")
        except Exception:
            pass

        # Migration: Add auth_provider if not exists
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'google'")
        except Exception:
            pass

        # Migration: Add last_login_at if not exists
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP")
        except Exception:
            pass

        # Migration: Add picture if not exists
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN picture TEXT")
        except Exception:
            pass

        # Migration: Add Leaderboard Stats columns
        for col in ["total_wealth REAL DEFAULT 0", "total_cost REAL DEFAULT 0", "total_roi REAL DEFAULT 0", "last_synced TEXT"]:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col}")
            except Exception:
                pass

        # Migration: Add User Settings (JSON)
        try:
             cursor.execute("ALTER TABLE users ADD COLUMN settings TEXT")
        except Exception:
             pass
             
        # Migration: Add API Key (Encrypted/Raw)
        try:
             cursor.execute("ALTER TABLE users ADD COLUMN api_key TEXT")
        except Exception:
             pass

        # User Groups
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_groups (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'default', 
                name TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Group Targets (watched stocks/ETFs/CB)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_targets (
                id TEXT PRIMARY KEY,
                group_id TEXT NOT NULL,
                stock_id TEXT NOT NULL,
                stock_name TEXT,
                asset_type TEXT DEFAULT 'stock' CHECK(asset_type IN ('stock', 'etf', 'cb')),
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES user_groups(id) ON DELETE CASCADE,
                UNIQUE(group_id, stock_id)
            )
        """)
        
        # Migration: Add asset_type column if not exists (for existing DBs)
        try:
            cursor.execute("ALTER TABLE group_targets ADD COLUMN asset_type TEXT DEFAULT 'stock'")
        except Exception:
            pass  # Column already exists
        
        # Transactions (buy, sell, dividend)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                target_id TEXT NOT NULL,
                type TEXT CHECK(type IN ('buy', 'sell', 'dividend')) NOT NULL,
                shares INTEGER NOT NULL,
                price REAL NOT NULL,
                date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (target_id) REFERENCES group_targets(id) ON DELETE CASCADE
            )
        """)
        
        # Dividend History (for tracking dividend payments)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dividend_history (
                id TEXT PRIMARY KEY,
                target_id TEXT NOT NULL,
                ex_date TEXT NOT NULL,
                pay_date TEXT,
                amount_per_share REAL NOT NULL,
                shares_held INTEGER NOT NULL,
                total_cash REAL NOT NULL,
                synced_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (target_id) REFERENCES group_targets(id) ON DELETE CASCADE,
                UNIQUE(target_id, ex_date)
            )
        """)
        
        # Activity Log (for tracking user activity by platform)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                platform TEXT CHECK(platform IN ('web', 'mobile')) NOT NULL,
                action TEXT DEFAULT 'login',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Race Cache (Historical Prices for My Race)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS race_cache (
                stock_id TEXT NOT NULL,
                month TEXT NOT NULL, -- YYYY-MM
                close_price REAL NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (stock_id, month)
            )
        """)

        # Notifications (Premium Rebalancing Alerts)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                type TEXT CHECK(type IN ('GRAVITY', 'SIZE', 'YIELD')) NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                link TEXT, -- URL link for notification action
                target_id TEXT, -- Optional link to stock
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Migration: Add link column to notifications (for existing DBs)
        try:
            cursor.execute("ALTER TABLE notifications ADD COLUMN link TEXT")
        except Exception:
            pass  # Column already exists
        
        # Migration: Add subscription_tier to users
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN subscription_tier INTEGER DEFAULT 0")
        except Exception:
            pass  # Column already exists

        # Migration: Add is_initialized to users (for default portfolio)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_initialized BOOLEAN DEFAULT 0")
        except Exception:
            pass

        # VIP/Premium Memberships (Injected via Admin)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_memberships (
                email TEXT PRIMARY KEY,
                tier TEXT NOT NULL, -- 'PREMIUM' or 'VIP'
                valid_until TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                injected_by TEXT
            )
        """)
        
        # --- Performance Indices ---
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_group_targets_group_id ON group_targets(group_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_target_id ON transactions(target_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dividend_history_target_id ON dividend_history(target_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)")

        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print(f"[Portfolio DB] Initialized at {DB_PATH}")
