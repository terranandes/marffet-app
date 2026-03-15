# BUG-021-PL_auth_account_switch_failure.md

# Bug Report: Auth Account Switch Failure (`?error=auth_failed`)

**Issue ID:** BUG-021
**Reporter:** `[PL]` (confirmed by BOSS Terran via screenshot)
**Date:** 2026-03-15
**Status:** ✅ FIXED (commit `c1a2b97`)
**Component:** Authentication / Session Management
**Severity:** High (Blocks account switching in production)

---

## Description

When a user logs out of `terranstock@gmail.com` and immediately logs in with `terranfund@gmail.com`, the app redirects to `/?error=auth_failed`.

Screenshot evidence: URL showed `marffet-app.zeabur.app/?error=auth_failed`.

---

## Root Cause

**Race condition in `UserContext.tsx` logout flow.**

The `logout()` function used fire-and-forget for the server session clear:

```js
// BROKEN:
fetch('/auth/logout', { method: 'GET' }).catch(() => {}); // Non-blocking!
router.push('/'); // Redirects IMMEDIATELY before server clears session
```

Sequence of failure:
1. Frontend fires `fetch('/auth/logout')` — not awaited
2. User is redirected to `/` and immediately clicks Login
3. `/auth/login` writes **new OAuth `state` nonce** into the **still-active stale session**
4. Server session finally gets cleared (too late — nonce is now orphaned)
5. Google returns to `/auth/callback` → `authorize_access_token` fails to validate `state` → **`auth_failed`**

---

## Fix Applied

### Fix 1 — `frontend/src/lib/UserContext.tsx`

Changed fire-and-forget to `await`:
```js
// FIXED:
await fetch('/auth/logout', { method: 'GET', credentials: 'include' });
router.push('/'); // Redirects ONLY AFTER session is cleared
```

### Fix 2 — `app/auth.py` `/logout` endpoint

- Returns **`200 JSON {"status": "ok"}`** for `fetch()` calls (previously returned a 302 redirect which caused `await fetch()` to follow the redirect rather than resolve cleanly in some environments)
- Explicitly calls `delete_cookie("session", ...)` to immediately purge the session cookie in the browser

---

## Affected Files
- `frontend/src/lib/UserContext.tsx` — logout() function
- `app/auth.py` — `/auth/logout` endpoint

## Verification Steps
1. Log in as `terranstock@gmail.com`
2. Click Sign Out
3. Click Login → Choose `terranfund@gmail.com`
4. Expect: Successful login as `terranfund@gmail.com` ✅
