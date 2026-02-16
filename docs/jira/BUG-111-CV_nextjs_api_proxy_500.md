# BUG-111-CV: Next.js API Proxy Returns 500 Errors

**Reporter:** [CV] (AntiGravity Code Verification Agent)
**Discovered:** 2026-02-09 23:37 HKT
**Severity:** High
**Component:** Frontend API Routing

## Description

The Next.js frontend routes API calls (`/api/*`) through its own server (port 3001) instead of directly to the Python backend (port 8001). This causes 500 Internal Server Errors.

## Affected Endpoints

- `/auth/me` → 500 (called twice on page load)
- `/api/portfolio/groups` → 500
- `/api/portfolio/targets?group_id=auth_check` → 500
- `/api/portfolio/dividends/total` → 500

## Root Cause Analysis

The frontend has API route handlers in `frontend/src/app/api/` or `frontend/src/pages/api/` that are catching requests instead of letting them pass through to `NEXT_PUBLIC_API_URL`.

OR

The Next.js `rewrites()` in `next.config.mjs` may not be correctly proxying `/api/*` to the backend.

## Steps to Reproduce

1. Start worktree backend on port 8001
2. Start worktree frontend on port 3001 with `.env` having `NEXT_PUBLIC_API_URL=http://localhost:8001`
3. Navigate to `http://localhost:3001/portfolio`
4. Observe console errors showing requests to `/api/portfolio/groups` hitting port 3001 (not 8001)

## Expected Behavior

API calls should route directly to `NEXT_PUBLIC_API_URL` (http://localhost:8001).

## Evidence

Screenshot: `tests/evidence/portfolio_empty_local.png`

Console log snippet:
```
[ERROR] Failed to load resource: the server responded with a status of 500 (Internal Server Error) @ http://localhost:3001/api/portfolio/groups:0
```

## Suggested Fix

Check `frontend/next.config.mjs` for `rewrites()` configuration and ensure `/api/*` routes are properly proxied.

---

## Resolution (2026-02-16)

**Investigator:** [CV] (AntiGravity)

### Root Cause: Port Mismatch (Configuration/Operational Issue — NOT a Code Bug)

| Component | Config | Actual (Worktree) |
|-----------|--------|-------------------|
| Backend default port | `uvicorn.run(port=8000)` | Running on **8001** |
| Frontend `.env.local` | `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000` | Proxying to **8000** |

When the frontend proxy (`next.config.ts` `rewrites()`) forwards `/api/*` to port 8000 but the backend is on 8001, Next.js returns **500 Internal Server Error** because the upstream fetch fails.

### Verified
1. ✅ `next.config.ts` rewrites are correct (`/api/:path*` → `${API_URL}/api/:path*`, `/auth/:path*` → `${API_URL}/auth/:path*`)
2. ✅ No conflicting Next.js API route handlers exist (no `frontend/src/app/api/` directory)
3. ✅ No Next.js middleware intercepting requests
4. ✅ All backend endpoints exist: `/auth/me` (L282), `/api/portfolio/groups` (L1084), etc.
5. ✅ `API_BASE = ""` in all frontend files → all calls use relative paths → go through rewrites (correct behavior)

### Fix
- **For local dev:** Ensure `.env.local` port matches the running backend port. Default is 8000.
- **For worktree dev:** Create worktree-specific `.env.local` with correct port.
- **Status:** RESOLVED (Configuration)
