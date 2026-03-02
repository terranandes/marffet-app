
import sqlite3
import uuid
from typing import Optional, List, Dict, Any

def update_user_login(conn: sqlite3.Connection, user_id: str, email: str, name: str, picture: str, provider: str = 'google') -> None:
    """Update user login info or create new user."""
    cursor = conn.cursor()
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if cursor.fetchone():
        cursor.execute("""
            UPDATE users 
            SET email = ?, name = ?, picture = ?, auth_provider = ?, last_login_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (email, name, picture, provider, user_id))
    else:
        cursor.execute("""
            INSERT INTO users (id, email, name, picture, auth_provider, last_login_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_id, email, name, picture, provider))

def update_user_nickname(conn: sqlite3.Connection, user_id: str, nickname: str) -> bool:
    """Update user nickname for leaderboard."""
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET nickname = ? WHERE id = ?", (nickname, user_id))
    return cursor.rowcount > 0

def upsert_user_stats(conn: sqlite3.Connection, user_id: str, total_wealth: float, total_cost: float, total_roi: float) -> None:
    """Update user statistics for leaderboard."""
    cursor = conn.cursor()
    # Try UPDATE first
    cursor.execute("""
        UPDATE users 
        SET total_wealth = ?, total_cost = ?, total_roi = ?, last_synced = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (total_wealth, total_cost, total_roi, user_id))
    
    if cursor.rowcount == 0:
        cursor.execute("""
            INSERT INTO users (id, total_wealth, total_cost, total_roi, last_synced)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_id, total_wealth, total_cost, total_roi))

def get_leaderboard(conn: sqlite3.Connection, limit: int = 50) -> List[Dict[str, Any]]:
    """Get top users by ROI."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            id, 
            nickname, 
            picture as avatar, 
            total_roi as roi, 
            total_wealth as market_value, 
            total_cost,
            last_synced
        FROM users
        WHERE total_cost > 1000  -- Minimum invested capital to qualify
        AND total_roi IS NOT NULL
        ORDER BY total_roi DESC
        LIMIT ?
    """, (limit,))
    return [dict(row) for row in cursor.fetchall()]

def get_user_profile(conn: sqlite3.Connection, user_id: str) -> Optional[Dict[str, Any]]:
    """Get basic user profile."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nickname, name, picture, total_wealth, total_cost, total_roi, last_synced, 
               created_at, COALESCE(subscription_tier, 0) as subscription_tier 
        FROM users WHERE id = ?
    """, (user_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def log_activity(conn: sqlite3.Connection, user_id: str, platform: str, action: str = 'login') -> str:
    """Log user activity."""
    if platform not in ('web', 'mobile'):
        platform = 'web'
    
    log_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO activity_log (id, user_id, platform, action) VALUES (?, ?, ?, ?)",
        (log_id, user_id, platform, action)
    )
    return log_id

def get_admin_metrics(conn: sqlite3.Connection, gm_emails: set = None, premium_emails: set = None, vip_emails: set = None) -> Dict[str, Any]:
    """Get admin dashboard metrics. Merges static users.subscription_tier with dynamic user_memberships and env var overrides."""
    cursor = conn.cursor()
    
    # Total users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    # Active users (30d)
    cursor.execute("""
        SELECT platform, COUNT(DISTINCT user_id) as count
        FROM activity_log
        WHERE created_at >= datetime('now', '-30 days')
        GROUP BY platform
    """)
    active_by_platform = {row['platform']: row['count'] for row in cursor.fetchall()}
    
    # Tier counting: merge static subscription_tier + dynamic user_memberships + env var overrides
    # Tier levels: 0=free, 1=premium, 2=vip, 3=gm
    
    # Step 1: Get all user emails and their static DB tier
    cursor.execute("""
        SELECT email, COALESCE(subscription_tier, 0) as tier
        FROM users
    """)
    user_tiers = {}
    for row in cursor.fetchall():
        user_tiers[row['email']] = row['tier']
    
    # Step 2: Overlay active injected memberships (higher tier wins)
    tier_name_to_level = {'PREMIUM': 1, 'VIP': 2}
    try:
        cursor.execute("""
            SELECT email, tier FROM user_memberships
            WHERE valid_until > datetime('now')
        """)
        for row in cursor.fetchall():
            email = row['email']
            injected_level = tier_name_to_level.get(row['tier'], 0)
            current_level = user_tiers.get(email, 0)
            if injected_level > current_level:
                user_tiers[email] = injected_level
    except Exception:
        pass  # user_memberships table may not exist yet
    
    # Step 3: Overlay env var emails (highest precedence: GM > VIP > PREMIUM)
    if gm_emails:
        for email in gm_emails:
            if email and email in user_tiers:
                user_tiers[email] = 3  # GM
    if vip_emails:
        for email in vip_emails:
            if email and email in user_tiers and user_tiers[email] < 2:
                user_tiers[email] = 2  # VIP
    if premium_emails:
        for email in premium_emails:
            if email and email in user_tiers and user_tiers[email] < 1:
                user_tiers[email] = 1  # PREMIUM
    
    # Step 4: Count tiers (GM excluded from premium/vip counts — separate admin tier)
    tier_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for level in user_tiers.values():
        if level in tier_counts:
            tier_counts[level] += 1
    
    return {
        "total_users": total_users,
        "active_users_web": active_by_platform.get('web', 0),
        "active_users_mobile": active_by_platform.get('mobile', 0),
        "subscription_tiers": {
            "free": tier_counts.get(0, 0),
            "premium": tier_counts.get(1, 0),
            "vip": tier_counts.get(2, 0)
        }
    }

def get_unread_notifications(conn: sqlite3.Connection, user_id: str) -> List[Dict[str, Any]]:
    """Get unread notifications for user."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, message, type, created_at, link
        FROM notifications
        WHERE user_id = ? AND is_read = 0
        ORDER BY created_at DESC
    """, (user_id,))
    return [dict(row) for row in cursor.fetchall()]

def mark_notification_read(conn: sqlite3.Connection, notification_id: str, user_id: str) -> bool:
    """Mark notification as read."""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications
        SET is_read = 1
        WHERE id = ? AND user_id = ?
    """, (notification_id, user_id))
    return cursor.rowcount > 0

def create_notification(conn: sqlite3.Connection, user_id: str, type: str, title: str, message: str, link: str = None, target_id: str = None) -> str:
    """Create a new notification."""
    notif_id = str(uuid.uuid4())
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notifications (id, user_id, type, title, message, link, target_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (notif_id, user_id, type, title, message, link, target_id))
    conn.commit()  # Commit immediately
    return notif_id

def get_user_public_profile(conn: sqlite3.Connection, user_id: str) -> Optional[Dict[str, Any]]:
    """Get public profile for a user."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nickname, picture, total_roi, last_synced
        FROM users WHERE id = ?
    """, (user_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def update_user_settings(conn: sqlite3.Connection, user_id: str, settings: str, api_key: str = None) -> bool:
    """Update user settings and api_key."""
    cursor = conn.cursor()
    # Note: settings is a JSON string
    if api_key is None:
        cursor.execute("UPDATE users SET settings = ? WHERE id = ?", (settings, user_id))
    else:
        cursor.execute("UPDATE users SET settings = ?, api_key = ? WHERE id = ?", (settings, api_key, user_id))
    return cursor.rowcount > 0

def get_user_settings(conn: sqlite3.Connection, user_id: str) -> Optional[Dict[str, Any]]:
    """Get user settings."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT settings, api_key FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return {"settings": row["settings"], "api_key": row["api_key"]}
    except Exception:
        return None
    return None
