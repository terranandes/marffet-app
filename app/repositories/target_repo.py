
import sqlite3
import uuid
from typing import List, Dict, Any, Optional

def add_target(conn: sqlite3.Connection, group_id: str, stock_id: str, stock_name: Optional[str] = None, asset_type: str = "stock") -> Dict[str, Any]:
    """Add a target to a group."""
    target_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO group_targets (id, group_id, stock_id, stock_name, asset_type) VALUES (?, ?, ?, ?, ?)",
        (target_id, group_id, stock_id, stock_name, asset_type)
    )
    return {
        "id": target_id, 
        "group_id": group_id, 
        "stock_id": stock_id, 
        "stock_name": stock_name, 
        "asset_type": asset_type
    }

def list_targets(conn: sqlite3.Connection, group_id: str) -> List[Dict[str, Any]]:
    """List all targets in a group."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, stock_id, stock_name, asset_type, added_at FROM group_targets WHERE group_id = ? ORDER BY added_at",
        (group_id,)
    )
    return [dict(row) for row in cursor.fetchall()]

def delete_target(conn: sqlite3.Connection, target_id: str) -> bool:
    """Delete a target."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("DELETE FROM group_targets WHERE id = ?", (target_id,))
    return cursor.rowcount > 0

def get_targets_by_user(conn: sqlite3.Connection, user_id: str) -> List[Dict[str, Any]]:
    """Get all targets for a user across all groups."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT gt.*, ug.name as group_name
        FROM group_targets gt
        JOIN user_groups ug ON gt.group_id = ug.id
        WHERE ug.user_id = ?
        ORDER BY gt.asset_type, gt.added_at
    """, (user_id,))
    return [dict(row) for row in cursor.fetchall()]

def update_target_name(conn: sqlite3.Connection, target_id: str, stock_name: str) -> None:
    """Update target stock name (for self-healing)."""
    conn.execute("UPDATE group_targets SET stock_name = ? WHERE id = ?", (stock_name, target_id))

def count_targets_in_group(conn: sqlite3.Connection, group_id: str) -> int:
    """Count targets in a group."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM group_targets WHERE group_id = ?", (group_id,))
    return cursor.fetchone()[0]

def get_target(conn: sqlite3.Connection, target_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific target."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM group_targets WHERE id = ?", (target_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def get_all_unique_stock_ids(conn: sqlite3.Connection) -> List[str]:
    """Get list of all unique stock IDs tracked by any user."""
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT stock_id FROM group_targets")
    return [row['stock_id'] for row in cursor.fetchall()]
