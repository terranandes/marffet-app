# Plan: VIP and Premium Membership Injection

## Goal
Implement a manual VIP and Premium membership injection system via the Admin Dashboard. This allows Game Masters (GMs) to grant premium access to users based on their Google Account email for specific durations (monthly or annually), laying the groundwork for future in-app subscriptions.

## User Review Required
- **Database Choice:** We propose storing this in `portfolio.db` (SQLite) since it's user-state data, rather than `market.duckdb` (which is rebuilt often). Is this acceptable?
- **Expiration Behavior:** When membership expires, the user will silently revert to a free tier. Do we need any "grace period" logic, or is strict expiration fine?

## Proposed Changes

### Backend (FastAPI & SQLite)

#### `app/repo/portfolio_db.py`
- Add a new table creation statement in `init_db()`:
```sql
CREATE TABLE IF NOT EXISTS user_memberships (
    email TEXT PRIMARY KEY,
    tier TEXT NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    injected_by TEXT
);
```

#### `app/api/auth.py`
- Modify the `/api/auth/me` endpoint.
- Currently, it sets `is_premium = user_email in GM_EMAILS or user_email in PREMIUM_EMAILS`.
- Update it to query the `user_memberships` table. If the email exists and `valid_until > datetime.now()`, grant `is_premium = True` and attach the `tier` (VIP/PREMIUM) to the response.

#### `app/api/admin.py` (or similar admin router)
- Add `POST /api/admin/memberships` to create/update a membership:
  - Validates GM access.
  - Takes `{ email: str, tier: str, duration_months: int }`.
  - Upserts into `user_memberships` setting `valid_until = now + duration_months`.
- Add `GET /api/admin/memberships` to list all memberships.
- Add `DELETE /api/admin/memberships/{email}` to manually revoke.

---

### Frontend (Next.js & React)

#### `frontend/src/app/admin/page.tsx`
- Add a new "Membership Management" section.
- **Form:**
  - Input: Google Account Email.
  - Select: Tier (`PREMIUM`, `VIP`).
  - Select: Duration (1 Month, 12 Months).
  - Button: "Inject Membership" (triggers `POST`).
- **Table:**
  - Displays currently active memberships (Email, Tier, Valid Until, Injected By).
  - Includes a "Revoke" (🗑️) button.

#### `frontend/src/services/adminService.ts`
- Add API bindings: `injectMembership`, `getMemberships`, `revokeMembership`.

## Verification Plan

### Automated Tests
- Run the full suite using existing scripts: `bash run_test.sh` or `python tests/integration/test_all_tabs.py` to ensure no regression.
- Since admin logic isn't heavily unit-tested presently, we will rely primarily on manual verification for the new admin UI features.

### Manual Verification
1. Log in as a GM.
2. Navigate to `/admin`.
3. Use the **Membership Management** section to inject 'PREMIUM' for `testuser@example.com` for 1 month.
4. Verify the user appears in the active members list with the correct expiration date.
5. Log out, then log in as `testuser@example.com` (using a mock or actual test account if available locally) and verify the Settings Modal reflects the Premium status.
6. Return to Admin as GM and click 'Revoke'. Verify the user disappears from the list, and falls back to Free Tier on their next auth check.
