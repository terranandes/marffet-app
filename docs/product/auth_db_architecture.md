# Auth & Database Architecture (Post-Recovery)
**Date:** 2026-01-27
**Status:** Stable / Production-Ready

This document outlines the architecture decisions made during the "Firefighting" phase to resolve Login Loops, Cookie Mismatches, and Schema Crashes.

## 1. Authentication Architecture (Dual-UI Support)

We support two distinct UIs accessing the same Backend Logic:
1.  **Next.js Frontend**: `martian-app.zeabur.app` (Port 3000 locally)
2.  **Legacy Backend UI**: `martian-api.zeabur.app` (Port 8000 locally)

### The Cookie Strategy
- **Problem**: Enforcing `Domain=martian-app.zeabur.app` breaks the Legacy UI (Cross-Domain).
- **Solution**: We use `COOKIE_DOMAIN = None` (Host Only).
    - When User visits `martian-app`, cookie is set for `martian-app` (valid).
    - When User visits `martian-api`, cookie is set for `martian-api` (valid).
    - **Result**: Both UIs work independently.

### The Rewrite Code Flow
To prevent CORS issues and "Third-Party Cookie" blocks:
1.  Frontend uses **Relative Links** (`/auth/login`, `/auth/logout`).
2.  Next.js Rewrites (`next.config.ts`) proxy these requests to the Backend.
3.  The User remains on the Frontend Domain (Difference hidden by proxy).
4.  Cookies are set on the Frontend Domain (First-Party).

---

## 2. Database Self-Healing Strategy (The "User Concern")

We use a **"Startup Migration"** pattern to ensure the database schema on Zeabur (Persistent Volume) is always up-to-date with the code.

### How it Works
On every application startup (`lifespan` in `main.py` -> `init_db` in `portfolio_db.py`), we execute:

```python
try:
    cursor.execute("ALTER TABLE users ADD COLUMN auth_provider ...")
except:
    pass # Column already exists
```

### Addressing Performance Concerns
**Q: Does this inspect the whole database every time?**
**A: NO.**
- SQLite's `ALTER TABLE ADD COLUMN` is an **O(1) operation** (Constant Time).
- It typically modifies the Schema Metadata only. It does **not** rewrite the table rows (unless adding a default value that requires calculation, but even then it's optimized in modern SQLite).
- If the column exists, the statement fails immediately (Microseconds).
- **Impact**: Zero. The server start time is unaffected, regardless of database size.

### Safety
- **Non-Destructive**: `ADD COLUMN` never deletes data.
- **Idempotent**: Running it 100 times has the same effect as running it once.

## 3. Deployment & Recovery
- **Codebase**: `master` branch is the source of truth.
- **Database**: 
    - **Local**: `app/portfolio.db` (Git-tracked seed).
    - **Remote**: `/data/portfolio.db` (Persistent Volume).
- **Sync**: When new code (with new columns) is pushed, Zeabur rebuilds -> App Starts -> `init_db` runs -> Missing columns are added to `/data/portfolio.db` automatically.

**Conclusion:** The system is robust, self-healing, and performant.

## 4. Access Tier Matrix (Premium & Admin)

The backend enforces a three-tier access model using environment variables:

| Env Var | Role | Powers |
|:---|:---|:---|
| `GM_EMAILS` | Admin (Game Master) | Full admin panel + premium features |
| `PREMIUM_EMAILS` | Premium User | Premium features only (no admin panel) |
| *(neither)* | Free User | Standard features |

### Implementation (`auth.py`)
```python
GM_EMAILS = set(email.strip().lower() for email in os.getenv('GM_EMAILS', '').split(',') if email.strip())
PREMIUM_EMAILS = set(email.strip().lower() for email in os.getenv('PREMIUM_EMAILS', '').split(',') if email.strip())

# /me endpoint logic:
is_admin = email in GM_EMAILS
is_premium = is_admin or email in PREMIUM_EMAILS
```

### Frontend Sync
- On login, `Sidebar.tsx` reads `/me` response → sets `localStorage("martian_premium")` if `is_premium` is true.
- `SettingsModal.tsx` shows "⭐ Premium Active" badge for non-admin premium users.
- Premium status is server-authoritative — `localStorage` is a convenience cache, not the source of truth.

### Deployment
- Both `GM_EMAILS` and `PREMIUM_EMAILS` must be configured in Zeabur backend env vars (`.env` is gitignored).
- Format: Comma-separated, case-insensitive. E.g., `PREMIUM_EMAILS=user1@gmail.com,user2@gmail.com`
