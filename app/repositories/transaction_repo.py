
import sqlite3
import uuid
from typing import List, Dict, Any

def add_transaction(conn: sqlite3.Connection, target_id: str, tx_type: str, shares: int, price: float, tx_date: str) -> Dict[str, Any]:
    """Add a transaction."""
    tx_id = str(uuid.uuid4())
    conn.execute(
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

def list_transactions(conn: sqlite3.Connection, target_id: str) -> List[Dict[str, Any]]:
    """List transactions for a target."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, type, shares, price, date FROM transactions WHERE target_id = ? ORDER BY date DESC",
        (target_id,)
    )
    return [dict(row) for row in cursor.fetchall()]

def update_transaction(conn: sqlite3.Connection, tx_id: str, tx_type: str, shares: int, price: float, tx_date: str) -> bool:
    """Update a transaction."""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transactions 
        SET type = ?, shares = ?, price = ?, date = ?
        WHERE id = ?
    """, (tx_type, shares, price, tx_date, tx_id))
    return cursor.rowcount > 0

def delete_transaction(conn: sqlite3.Connection, tx_id: str) -> bool:
    """Delete a transaction."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    return cursor.rowcount > 0

def get_user_transactions(conn: sqlite3.Connection, user_id: str) -> List[Dict[str, Any]]:
    """Get all transactions for a user (for bulk calculations)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.target_id, t.type, t.shares, t.price, t.date, gt.stock_id
        FROM transactions t
        JOIN group_targets gt ON t.target_id = gt.id
        JOIN user_groups ug ON gt.group_id = ug.id
        WHERE ug.user_id = ?
        ORDER BY t.date ASC
    """, (user_id,))
    return [dict(row) for row in cursor.fetchall()]

def count_transactions(conn: sqlite3.Connection, target_id: str) -> int:
    """Count transactions for a target."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE target_id = ?", (target_id,))
    return cursor.fetchone()[0]

def get_transaction(conn: sqlite3.Connection, tx_id: str) -> Dict[str, Any]:
    """Get a specific transaction."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def get_dividend_history(conn: sqlite3.Connection, target_id: str) -> List[Dict[str, Any]]:
    """Get dividend history for a target."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, ex_date, shares_held, total_cash, amount_per_share 
        FROM dividend_history WHERE target_id = ? 
        ORDER BY ex_date DESC
    """, (target_id,))
    return [dict(row) for row in cursor.fetchall()]

def get_all_dividends_for_user(conn: sqlite3.Connection, user_id: str) -> List[Dict[str, Any]]:
    """Get all dividends for a user."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT dh.ex_date as date, dh.total_cash, gt.stock_id, dh.amount_per_share, dh.target_id
        FROM dividend_history dh
        JOIN group_targets gt ON dh.target_id = gt.id
        JOIN user_groups ug ON gt.group_id = ug.id
        WHERE ug.user_id = ?
        ORDER BY dh.ex_date ASC
    """, (user_id,))
    return [dict(row) for row in cursor.fetchall()]

def upsert_dividend(conn: sqlite3.Connection, div_id: str, target_id: str, ex_date: str, amount: float, shares: float, total: float) -> None:
    """Upsert a dividend record."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO dividend_history (id, target_id, ex_date, amount_per_share, shares_held, total_cash)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            shares_held = excluded.shares_held,
            total_cash = excluded.total_cash,
            amount_per_share = excluded.amount_per_share
    """, (div_id, target_id, ex_date, amount, shares, total))

def delete_dividend(conn: sqlite3.Connection, div_id: str) -> bool:
     conn.execute("DELETE FROM dividend_history WHERE id = ?", (div_id,))
     return True
