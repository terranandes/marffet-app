"""
User Feedback & Bug Report Database Module
Handles storage and retrieval of user-submitted feedback/bug reports.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime

# Use same DB as portfolio
DB_PATH = Path(__file__).parent / "portfolio.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(str(DB_PATH), timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_feedback_table():
    """Create user_feedback table if not exists"""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                user_email TEXT,
                feature_category TEXT NOT NULL,
                feature_name TEXT,
                feedback_type TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'new',
                agent_notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT
            )
        """)
        conn.commit()


# Feature categories for hierarchical display
FEATURE_CATEGORIES = {
    "mars_strategy": {
        "name": "Mars Strategy",
        "description": "Search and filter stocks using the Mars Strategy (Top 50 performers with low volatility)",
        "features": ["Search", "Filter", "Sort", "Stock Details", "Simulation"]
    },
    "bar_chart_race": {
        "name": "Bar Chart Race",
        "description": "Animated visualization of wealth growth over time",
        "features": ["Play/Pause", "Speed Control", "Metric Selection"]
    },
    "portfolio": {
        "name": "Portfolio",
        "description": "Track your real investments with groups and transactions",
        "features": ["Add Group", "Add Stock", "Record Transaction", "View Summary"]
    },
    "trend": {
        "name": "Trend Dashboard",
        "description": "Monthly cost trend and portfolio breakdown",
        "features": ["Trend Chart", "Month Selection", "Live Prices"]
    },
    "my_race": {
        "name": "My Portfolio Race",
        "description": "Watch your investments race against each other",
        "features": ["Play Animation", "Asset Stats"]
    },
    "ai_copilot": {
        "name": "AI Copilot (Mars AI)",
        "description": "AI-powered investment assistant",
        "features": ["Chat", "Portfolio Analysis", "Premium Advice"]
    },
    "leaderboard": {
        "name": "Leaderboard",
        "description": "Community rankings and public profiles",
        "features": ["View Rankings", "Public Profile", "Nickname"]
    },
    "settings": {
        "name": "Settings",
        "description": "App configuration and preferences",
        "features": ["API Key", "Language", "Premium Toggle"]
    },
    "cash_ladder": {
        "name": "Cash Ladder",
        "description": "Cash flow ladder and allocation analysis",
        "features": ["Ladder Chart", "Allocation Breakdown"]
    },
    "compound_interest": {
        "name": "Compound Interest",
        "description": "Compound interest simulator and comparison tool",
        "features": ["Simulation", "BAO/BAH/BAL Comparison", "ECharts Visualization"]
    }
}


def submit_feedback(user_id: str, user_email: str, category: str, 
                   feedback_type: str, message: str, feature_name: str = None) -> dict:
    """Submit a new feedback/bug report"""
    init_feedback_table()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_feedback 
            (user_id, user_email, feature_category, feature_name, feedback_type, message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, user_email, category, feature_name, feedback_type, message))
        conn.commit()
        
        return {
            "success": True,
            "id": cursor.lastrowid,
            "message": "Feedback submitted successfully"
        }


def get_all_feedback(status_filter: str = None) -> list:
    """Get all feedback (for GM review)"""
    init_feedback_table()
    
    with get_db() as conn:
        if status_filter:
            rows = conn.execute("""
                SELECT * FROM user_feedback 
                WHERE status = ?
                ORDER BY created_at DESC
            """, (status_filter,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM user_feedback 
                ORDER BY created_at DESC
            """).fetchall()
        
        return [dict(row) for row in rows]


def get_feedback_stats() -> dict:
    """Get feedback statistics for GM dashboard"""
    init_feedback_table()
    
    with get_db() as conn:
        stats = {}
        for status in ['new', 'reviewing', 'confirmed', 'fixed', 'wontfix']:
            count = conn.execute(
                "SELECT COUNT(*) FROM user_feedback WHERE status = ?", 
                (status,)
            ).fetchone()[0]
            stats[status] = count
        
        stats['total'] = sum(stats.values())
        return stats


def update_feedback(feedback_id: int, status: str = None, agent_notes: str = None) -> dict:
    """Update feedback status and/or notes (GM only)"""
    init_feedback_table()
    
    updates = []
    params = []
    
    if status:
        updates.append("status = ?")
        params.append(status)
    
    if agent_notes is not None:
        updates.append("agent_notes = ?")
        params.append(agent_notes)
    
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(feedback_id)
        
        with get_db() as conn:
            conn.execute(f"""
                UPDATE user_feedback 
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            conn.commit()
    
    return {"success": True, "id": feedback_id}


def get_feature_categories() -> dict:
    """Return feature categories for UI display"""
    return FEATURE_CATEGORIES
