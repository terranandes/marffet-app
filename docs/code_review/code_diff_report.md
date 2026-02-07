# Code Difference Report: `abc7ea7` vs `HEAD`

**Date:** 2026-01-27
**Purpose:** Review changes made to resolve Login Loop / Cookie Mismatch issues on Next.js Rewrite architecture.

## 1. Authentication Logic (`app/auth.py`)

### A. Redirect URI Robustness
- **Old (`abc7ea7`)**: Used `request.url_for` or Manual String manually.
- **New (`HEAD`)**: Forces `redirect_uri` to match `FRONTEND_URL` (e.g., `https://martian-app.zeabur.app`) to prevent mismatches when backend is accessed via internal `martian-api` host.
- **Why**: Google requires the `redirect_uri` sent during code exchange to MATCH the one used during initial redirect. The internal rewrite was causing a mismatch.

### B. Access Token Exchange
- **Old**: Explicitly passed `redirect_uri` to `authorize_access_token`.
- **New**: Removed explicit argument.
- **Why**: Authlib v1.6+ automatically retrieves the correct `redirect_uri` from the session state. Passing it explicitly caused a `TypeError: multiple values for argument` crash.

### C. Debugging
- **New**: Added `/auth/debug` endpoint features to inspect `Host` headers and `COOKIE_DOMAIN` resolution.

## 2. Server Configuration (`app/main.py`)

### A. Cookie Domain
- **Old**: `COOKIE_DOMAIN` was calculated manually or used defaults.
- **New**: Uses **Explicit Domain** strategy (forcing `martian-app.zeabur.app`) to ensure cookies set by the backend are accepted by the browser when viewing the frontend.
- **Why**: Solves `cookie_present: false` error on mobile/cross-site flows.

### B. Middleware
- **New**: Correctly ordered `SessionMiddleware` and `ProxyHeadersMiddleware` to ensure `https` scheme is detected correctly behind a proxy.

## 3. Database Schema (`app/portfolio_db.py`)

### A. New Column
- **New**: Added `auth_provider` column to `users` table schema.
- **Issue**: **Missing Migration**. The code adds the column to the `CREATE TABLE` definition, but does not migrate existing databases.
- **Result**: Local login fails with `table users has no column named auth_provider` because your local `portfolio.db` is older than this change.

## Recommendation
**Do NOT Revert.**
The "Auth Fixes" (1 & 2) are verified to be correct for the Rewrite architecture.
The current failure (3) is a simple **Local Database Schema Mismatch**.

I can fix the local error immediately by checking for and adding the missing column in `app/portfolio_db.py`. This will allow you to verify the login locally without undoing the Rewrite fixes.
