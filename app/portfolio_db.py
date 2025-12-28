"""
Portfolio Database Module

SQLite database for user portfolio feature:
- User groups (up to 5 for free tier)
- Group targets (up to 20 per group for free tier)
- Buy/Sell transactions with cost, shares, date
"""

import sqlite3
import uuid
from pathlib import Path
from datetime import date, datetime
from typing import Optional
from contextlib import contextmanager

# Database file location
DB_PATH = Path(__file__).parent / "portfolio.db"

# Tier limits
FREE_MAX_GROUPS = 11
FREE_MAX_TARGETS_PER_GROUP = 50
FREE_MAX_TX_PER_TARGET = 50


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Initialize database with schema."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # User Groups
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_groups (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'default',
                name TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Group Targets (watched stocks)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_targets (
                id TEXT PRIMARY KEY,
                group_id TEXT NOT NULL,
                stock_id TEXT NOT NULL,
                stock_name TEXT,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES user_groups(id) ON DELETE CASCADE,
                UNIQUE(group_id, stock_id)
            )
        """)
        
        # Transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                target_id TEXT NOT NULL,
                type TEXT CHECK(type IN ('buy', 'sell')) NOT NULL,
                shares INTEGER NOT NULL,
                price REAL NOT NULL,
                date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (target_id) REFERENCES group_targets(id) ON DELETE CASCADE
            )
        """)
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print(f"[Portfolio DB] Initialized at {DB_PATH}")


# ============== GROUP OPERATIONS ==============

def create_group(name: str, user_id: str = "default") -> dict:
    """Create a new portfolio group."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check limit
        cursor.execute("SELECT COUNT(*) FROM user_groups WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        if count >= FREE_MAX_GROUPS:
            raise ValueError(f"Maximum {FREE_MAX_GROUPS} groups allowed for free tier")
        
        group_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO user_groups (id, user_id, name) VALUES (?, ?, ?)",
            (group_id, user_id, name)
        )
        return {"id": group_id, "name": name, "user_id": user_id}


def list_groups(user_id: str = "default") -> list:
    """List all groups for a user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, created_at FROM user_groups WHERE user_id = ? ORDER BY created_at",
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def delete_group(group_id: str) -> bool:
    """Delete a group and all its targets/transactions."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("DELETE FROM user_groups WHERE id = ?", (group_id,))
        return cursor.rowcount > 0


# ============== TARGET OPERATIONS ==============

def add_target(group_id: str, stock_id: str, stock_name: Optional[str] = None) -> dict:
    """Add a stock target to a group."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check limit
        cursor.execute("SELECT COUNT(*) FROM group_targets WHERE group_id = ?", (group_id,))
        count = cursor.fetchone()[0]
        if count >= FREE_MAX_TARGETS_PER_GROUP:
            raise ValueError(f"Maximum {FREE_MAX_TARGETS_PER_GROUP} targets per group for free tier")
        
        target_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO group_targets (id, group_id, stock_id, stock_name) VALUES (?, ?, ?, ?)",
            (target_id, group_id, stock_id, stock_name)
        )
        return {"id": target_id, "group_id": group_id, "stock_id": stock_id, "stock_name": stock_name}


def list_targets(group_id: str) -> list:
    """List all targets in a group."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, stock_id, stock_name, added_at FROM group_targets WHERE group_id = ? ORDER BY added_at",
            (group_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def delete_target(target_id: str) -> bool:
    """Delete a target and all its transactions."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("DELETE FROM group_targets WHERE id = ?", (target_id,))
        return cursor.rowcount > 0


# ============== TRANSACTION OPERATIONS ==============

def add_transaction(target_id: str, tx_type: str, shares: int, price: float, tx_date: str) -> dict:
    """Add a buy/sell transaction."""
    if tx_type not in ('buy', 'sell'):
        raise ValueError("Transaction type must be 'buy' or 'sell'")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check transaction limit
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE target_id = ?", (target_id,))
        count = cursor.fetchone()[0]
        if count >= FREE_MAX_TX_PER_TARGET:
            raise ValueError(f"Maximum {FREE_MAX_TX_PER_TARGET} transactions per target for free tier")
        
        tx_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO transactions (id, target_id, type, shares, price, date) VALUES (?, ?, ?, ?, ?, ?)",
            (tx_id, target_id, tx_type, shares, price, tx_date)
        )
        return {
            "id": tx_id,
            "target_id": target_id,
            "type": tx_type,
            "shares": shares,
            "price": price,
            "date": tx_date
        }


def list_transactions(target_id: str) -> list:
    """List all transactions for a target."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, type, shares, price, date, created_at FROM transactions WHERE target_id = ? ORDER BY date",
            (target_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def delete_transaction(tx_id: str) -> bool:
    """Delete a transaction."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        return cursor.rowcount > 0


# ============== PORTFOLIO SUMMARY ==============

def get_target_summary(target_id: str, current_price: float = None) -> dict:
    """
    Calculate comprehensive summary for a single target.
    
    Returns:
        - total_shares: Net shares held
        - avg_cost: Average cost per share
        - total_cost: Total cost basis
        - realized_pnl: Realized P/L from completed sells
        - tx_count: Number of transactions
        - market_value: Current market value (if price provided)
        - unrealized_pnl: Unrealized P/L (if price provided)
        - unrealized_pnl_pct: % return (if price provided)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT type, shares, price FROM transactions WHERE target_id = ? ORDER BY date",
            (target_id,)
        )
        transactions = cursor.fetchall()
    
    total_shares = 0
    total_cost = 0.0
    realized_pnl = 0.0
    tx_count = len(transactions)
    
    for tx in transactions:
        if tx['type'] == 'buy':
            total_shares += tx['shares']
            total_cost += tx['shares'] * tx['price']
        else:  # sell
            sell_shares = tx['shares']
            sell_revenue = sell_shares * tx['price']
            if total_shares > 0:
                avg_cost_per_share = total_cost / total_shares
                cost_basis_sold = sell_shares * avg_cost_per_share
                realized_pnl += sell_revenue - cost_basis_sold
                total_shares -= sell_shares
                total_cost = max(0, total_shares * avg_cost_per_share)
    
    avg_cost = total_cost / total_shares if total_shares > 0 else 0
    
    result = {
        "total_shares": total_shares,
        "avg_cost": round(avg_cost, 2),
        "total_cost": round(total_cost, 2),
        "realized_pnl": round(realized_pnl, 2),
        "tx_count": tx_count
    }
    
    if current_price is not None and total_shares > 0:
        market_value = total_shares * current_price
        unrealized_pnl = market_value - total_cost
        unrealized_pnl_pct = (unrealized_pnl / total_cost * 100) if total_cost > 0 else 0
        
        result.update({
            "current_price": current_price,
            "market_value": round(market_value, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "unrealized_pnl_pct": round(unrealized_pnl_pct, 2)
        })
    
    return result


# ============== LIVE PRICE FETCHING ==============

def fetch_live_prices(stock_ids: list) -> dict:
    """
    Fetch live prices for Taiwan stocks using yfinance.
    Returns dict: {stock_id: {price, change, change_pct}}
    """
    import yfinance as yf
    
    prices = {}
    for sid in stock_ids:
        try:
            # Taiwan stocks have .TW or .TWO suffix
            ticker = f"{sid}.TW"
            stock = yf.Ticker(ticker)
            info = stock.fast_info
            
            current_price = info.get('lastPrice') or info.get('regularMarketPrice', 0)
            prev_close = info.get('previousClose', current_price)
            change = current_price - prev_close
            change_pct = (change / prev_close * 100) if prev_close else 0
            
            prices[sid] = {
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2)
            }
        except Exception as e:
            # Try .TWO for OTC stocks
            try:
                ticker = f"{sid}.TWO"
                stock = yf.Ticker(ticker)
                info = stock.fast_info
                current_price = info.get('lastPrice') or info.get('regularMarketPrice', 0)
                prev_close = info.get('previousClose', current_price)
                change = current_price - prev_close
                change_pct = (change / prev_close * 100) if prev_close else 0
                
                prices[sid] = {
                    "price": round(current_price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2)
                }
            except:
                prices[sid] = {"price": 0, "change": 0, "change_pct": 0, "error": str(e)}
    
    return prices


# Initialize on import
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
