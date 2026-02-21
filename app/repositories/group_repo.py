
import sqlite3
import uuid
from typing import List, Dict, Any

def create_group(conn: sqlite3.Connection, user_id: str, name: str) -> Dict[str, Any]:
    """Create a new portfolio group."""
    group_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO user_groups (id, user_id, name) VALUES (?, ?, ?)",
        (group_id, user_id, name)
    )
    return {"id": group_id, "name": name, "user_id": user_id}

def list_groups(conn: sqlite3.Connection, user_id: str) -> List[Dict[str, Any]]:
    """List all groups for a user."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, created_at FROM user_groups WHERE user_id = ? ORDER BY created_at",
        (user_id,)
    )
    return [dict(row) for row in cursor.fetchall()]

def delete_group(conn: sqlite3.Connection, group_id: str) -> bool:
    """Delete a group."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_groups WHERE id = ?", (group_id,))
    return cursor.rowcount > 0

def count_groups(conn: sqlite3.Connection, user_id: str) -> int:
    """Count groups for a user."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM user_groups WHERE user_id = ?", (user_id,))
    return cursor.fetchone()[0]

def check_initialized(conn: sqlite3.Connection, user_id: str) -> bool:
    """Check if user portfolio is initialized."""
    cursor = conn.cursor()
    cursor.execute("SELECT is_initialized FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    return bool(row[0]) if row else False

def mark_initialized(conn: sqlite3.Connection, user_id: str) -> None:
    """Mark user portfolio as initialized."""
    conn.execute("UPDATE users SET is_initialized = 1 WHERE id = ?", (user_id,))
