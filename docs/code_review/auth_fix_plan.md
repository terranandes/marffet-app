# Code Review & Auth Repair Plan (2026-01-26)

## Problem Summary
Users are unable to Login or Logout on `martian-app.zeabur.app`.
- **Logout Error (Fixed):** 500 error due to `NameError` (Import issue).
- **Login Error (Current):** `CSRF Warning! State not equal`. Debug info shows `cookie_present: false`.

## Root Cause Analysis
The primary issue is **Cookie Scope Mismatch** caused by the Next.js Rewrite architecture (`martian-app` -> `martian-api`).

### 1. `COOKIE_DOMAIN` Vulnerability
In `app/main.py`:
```python
parsed_frontend = urlparse(FRONTEND_URL_FOR_DETECTION)
COOKIE_DOMAIN = parsed_frontend.hostname if IS_PRODUCTION else None
```
- **Risk:** If `FRONTEND_URL` is configured as `martian-app.zeabur.app` (without `https://`), `urlparse` returns `hostname=None`.
- **Result:** `COOKIE_DOMAIN` becomes `None` (Host-Only).
- **Impact:** Since the backend receives requests via internal network (or rewritten host), it sets the cookie for the *backend host* (`martian-api`). The browser (on `martian-app`) ignores it.

### 2. Manual Response Bypass (Debug Cookie)
In `app/auth.py` (`login`):
```python
    response.set_cookie(
        key="debug_persist", 
        domain=None # Try Host-Only for this one to compare
    )
```
- **Risk:** Explicitly setting `domain=None` forces Host-Only.
- **Result:** Cookie set for `martian-api`.
- **Impact:** Browser on `martian-app` never sees the debug cookie, leading to `debug_cookie: null`.

### 3. Middleware Redundancy
In `app/main.py`:
- `ProxyHeadersMiddleware` is added TWICE (Line 92 and Line 151).
- This is sloppy but likely not the root cause. Removing the duplicate is recommended.

## Proposed Fixes

### A. Robust `COOKIE_DOMAIN` Logic
Updates `app/main.py` and `app/auth.py` to handle URLs without schemes.
```python
def get_domain(url):
    if not url.startswith("http"):
        url = "https://" + url
    return urlparse(url).hostname
```

### B. Consistent Cookie Scope
Update `app/auth.py`:
- Set `debug_persist` cookie uses `COOKIE_DOMAIN` (or explicit `martian-app.zeabur.app`) instead of `None`.

### C. Verification
- Add a new endpoint `/auth/config-check` to dump the *resolved* `COOKIE_DOMAIN` and `FRONTEND_URL` to help us verify the production environment state.

## Implementation Steps
1.  **Refactor `app/main.py`**: Fix `COOKIE_DOMAIN` calculation and remove duplicate middleware.
2.  **Refactor `app/auth.py`**: Update `login` to use the correct domain for debug cookie.
3.  **Deployment**: Push and verify.
