# Brainstorming: VIP and Premium Membership Injection

## 🎯 Purpose
The user wants to implement manual injection of VIP and Premium membership flags via the Admin Dashboard.
This allows the administrators to manually grant membership via a user's Google Account email, separated from static `.env` or Zeabur configurations.
It must support "monthly" and "annually" injection durations, setting a foundation for future in-app subscriptions.

## 👥 Users
- **Game Masters / Admins:** Will use the Admin Dashboard UI to inject memberships.
- **End Users:** Will receive premium features when their Google account email matches the injected active membership.

## 📦 Scope
**Must-have:**
- Database schema changes to store membership records (email, tier, expiration_date).
- Backend APIs to:
  1. Inject/grant membership (Admin only)
  2. Read current membership status (Admin view & User `GET /auth/me`)
- Admin Dashboard UI:
  - Form/Modal to input Email, select Tier (VIP/Premium), and Duration (1 Month / 1 Year).
  - List/Table of active manual memberships.
- Authorization: Ensure only GMs can inject memberships.
- Core App Logic: Update `is_premium` derivation in `/auth/me` to check the DB on top of the static `PREMIUM_EMAILS` env var.

**Nice-to-have:**
- Revoke membership.
- Audit logging of who injected what.

## 🧠 Architectural Decisions

### 1. Database Storage
**Question:** Where do we store the membership records?
**Options:**
- **A. DuckDB (`market.duckdb`):** Currently used for market prices and dividends, heavily optimized for read-heavy columnar data, wiped and rebuilt frequently.
- **B. SQLite (`app.db` / `portfolio.db`):** Currently used for Portfolios, Transactions, and User Data. Persistent, designed for OLTP.
**Decision:** **SQLite (`portfolio.db`)** is the correct place. We should create a new table `user_memberships` (or similar) here because it relates to user state, not market data.

### 2. Table Schema
```sql
CREATE TABLE memberships (
    email TEXT PRIMARY KEY,
    tier TEXT NOT NULL, -- 'PREMIUM', 'VIP'
    valid_until TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    injected_by TEXT -- GM email who granted it
);
```

### 3. Backend Integration (`/auth/me`)
Currently, `auth.py` determines `is_premium` by checking if the user's email is in `GM_EMAILS` or `PREMIUM_EMAILS` environment variables.
**Change:** When `/auth/me` is called, we must query the `memberships` table for the user's email. If a record exists and `valid_until > now()`, we set `is_premium = True` (or return the specific `tier`).

### 4. Admin API & UI
**API:**
- `POST /api/admin/memberships` (Requires GM auth). Body: `{"email": "...", "tier": "PREMIUM", "duration_months": 1 or 12}`
- `GET /api/admin/memberships` (Requires GM auth). Returns list of active memberships.

**UI (Admin Dashboard):**
- Add a new section: **"Membership Management"**
- A simple form with: Email input, Tier Dropdown (Premium/VIP), Duration Dropdown (1 Month / 1 Year), "Inject" button.
- A table showing active injected users and their expiration dates.
