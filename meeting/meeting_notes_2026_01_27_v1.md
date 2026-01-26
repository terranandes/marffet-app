# Agents Sync Meeting Notes
**Date:** 2026-01-27
**Attendees:** [PM], [PL], [SPEC], [CODE], [UI], [CV]

## 1. Project Progress ([PM])
- **Migration Status:** The migration from the legacy generic UI to the new **Next.js Frontend (martian-app)** is effectively **Complete** in terms of infrastructure.
- **Critical Milestone:** Authentication works across domains (Cross-Site) and via Rewrites.
- **Next Phase:** Focus shifts to **User Experience Polish** (Mobile Responsive) and **Feature Parity** (Portfolio Management).

## 2. Bug Triage & Fixes ([PL])
- **Auth Login Loop (BUG-009):** **FIXED**.
    - Root Cause: Explicit `COOKIE_DOMAIN` vs Host-Only mismatch behind Next.js Rewrite.
    - Solution: Enforced `COOKIE_DOMAIN` to match Frontend URL + Removed explicit `redirect_uri` in callback.
- **Local Crash (TypeError):** **FIXED**.
    - Removed redundant argument in `authorize_access_token`.
- **Local DB Crash (Schema):** **FIXED**.
    - Added missing migration for `auth_provider` column.
- **Logout Redirect:** **FIXED**.
    - Logout now redirects to `/` instead of forcing `FRONTEND_URL`, respecting the user's current origin (Backend vs Frontend).

## 3. Specification & Infrastructure ([SPEC])
- **Zeabur Deployment:**
    - Service `martian-app` (Next.js) handles UI and Rewrites `/api` -> `martian-api`.
    - Service `martian-api` (FastAPI) handles Logic and Auth.
- **Environment Variables:**
    - `FRONTEND_URL`: Must be set to `https://martian-app.zeabur.app` (Product) or `http://localhost:3000` (Dev).
    - `COOKIE_DOMAIN`: Dynamically parsed from `FRONTEND_URL`.
- **Build Pipeline:** `uv` based build verified.

## 4. Backend Implementation ([CODE])
- **Robustness:** Added `get_domain_from_url` to handle scheme-less URLs.
- **Debugging:** Added `/auth/debug` endpoint to inspect headers in production.
- **Logout:** Switched to "Nuclear Logout" (Clear Session + Cookie Deletion) and relative redirect.

## 5. UI/UX ([UI])
- **Mobile Layout:**
    - Initial feedback suggests better viewport handling is needed for the Login Overlay (BUG-008 resolved previously/in-progress).
    - Need to verify the Sidebar behavior on small screens.
- **Aesthetic:** Dark Mode default is working well.

## 6. Code Verification ([CV])
- **Review of Auth Changes:**
    - **Security:** CSRF protection via `SameSite=Lax` (implied/default) + Explicit Domain matching is secure.
    - **Logic:** `auth.py` is much cleaner now without circular dependencies.
    - **Risk:** High stability. The recent patches addressed the edge cases (Rewrite vs Direct).

## Action Items
1.  **[USER]**: Restart Backend (`./start_app.sh`) and Verify Local Login/Logout.
2.  **[USER/PL]**: Monitor Zeabur Logs for successful deploy.
3.  **[UI]**: Conduct full mobile walkthrough.

**Reported by:** [PL] Terran Wu
