# GM Admin Dashboard Feature

## Goal
Create a secure, GM-only admin page to view critical user and subscription metrics.

## Trigger Condition
User's email matches `terranfund@gmail.com` OR `terranandes@gmail.com`.

## User Review Required
> [!IMPORTANT]
> This feature introduces a **hardcoded email whitelist** for admin access. This is a simple approach for a small team. If the admin list grows, consider using a database flag (`is_admin`).

> [!CAUTION]
> Metrics like "Active Users (Past Month)" and "Subscription Tier" require new database schema columns to track `last_active_at` and `subscription_tier`. These are currently **not tracked**.

---

## Proposed Changes

### Environment Configuration

#### [MODIFY] [.env.example](file:///home/terwu01/github/martian/.env.example)
- Add `GM_EMAILS=terranfund@gmail.com,terranandes@gmail.com`.

---

### Backend API (`app/`)

#### [MODIFY] [auth.py](file:///home/terwu01/github/martian/app/auth.py)
- Load `GM_EMAILS` from environment variable (comma-separated).
- Add `get_admin_user` dependency that verifies `user['email']` is in `GM_EMAILS`.

#### [MODIFY] [portfolio_db.py](file:///home/terwu01/github/martian/app/portfolio_db.py)
- **Schema Migration**: Add `subscription_tier INTEGER DEFAULT 0` to `users` table.
- **New Table**: Create `activity_log` table:
  ```sql
  CREATE TABLE activity_log (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      platform TEXT CHECK(platform IN ('web', 'mobile')) NOT NULL,
      action TEXT DEFAULT 'login',
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id)
  )
  ```
- Add `log_activity(user_id, platform, action)` function.
- Add `get_admin_metrics()` function to query:
  - Total Registered Users (`COUNT(*) FROM users`)
  - Active Users by Platform (Last 30 Days) (`COUNT(DISTINCT user_id) FROM activity_log WHERE ...`)
  - Subscription breakdown by tier

#### [MODIFY] [main.py](file:///home/terwu01/github/martian/app/main.py)
- Add `GET /api/admin/metrics` endpoint protected by `get_admin_user`.
- Call `log_activity()` on relevant API calls to track activity.

---

### Frontend (`frontend/src/app/`)

#### [NEW] [admin/page.tsx](file:///home/terwu01/github/martian/frontend/src/app/admin/page.tsx)
- Create a new admin page.
- Displayed ONLY when user email is in whitelist (checked via `/auth/me` response).
- UI: Simple table/cards showing:
  - Registered Users Count
  - Active Users (Web/Mobile split - *pending data*)
  - Subscription Tiers (0/1/2)

#### [MODIFY] [layout.tsx](file:///home/terwu01/github/martian/frontend/src/app/layout.tsx)
- Add "GM Dashboard" nav link, conditionally visible when `user.email` is in whitelist.

---

## Verification Plan

### Automated Tests
1.  **API Test**: `uv run pytest tests/test_admin.py` (to be created).
2.  **Auth Check**: Ensure non-GM users get `403 Forbidden` on `/api/admin/metrics`.

### Manual Verification
1.  Login as `terranfund@gmail.com`.
2.  Verify "GM Dashboard" link appears in navigation.
3.  Navigate to `/admin` and view metrics.
