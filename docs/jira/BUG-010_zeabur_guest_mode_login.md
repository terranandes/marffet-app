# BUG-010: Zeabur Login Shows Guest Mode Despite Authenticated
**Reporter:** [CV] Agent
**Date:** 2026-01-28
**Severity:** Critical
**Environment:** Zeabur Next.js (martian-app.zeabur.app)

## Description
After successful Google Login on Zeabur Next.js UI:
- **Sidebar** correctly shows authenticated user (`terranstock@gmail...`)
- **Portfolio page** incorrectly shows "Guest Mode" badge
- **Portfolio data** shows "No groups yet" instead of user's actual portfolio

## Screenshot Evidence
![Bug Evidence](file:///home/terwu01/.gemini/antigravity/brain/b49fbb77-9d9c-4a6f-b522-53f3e307f306/uploaded_media_1769533011810.png)

## Symptoms
- Login appears successful (user shown in sidebar)
- Session cookie may not be reaching `/api/portfolio/groups`
- Frontend might be using different session detection for Portfolio vs Sidebar

## Potential Causes
1. **API Fetch not including credentials**: `fetch()` calls to `/api/portfolio/*` may not have `credentials: 'include'`
2. **Cross-domain cookie issue**: `martian-app` making API calls to `martian-api` without cookies
3. **Session check mismatch**: Portfolio page checks session differently than Sidebar

## Resolution
**Root Cause:** `portfolio/page.tsx` line 61 used `NEXT_PUBLIC_API_URL` for auth check, bypassing Next.js proxy. Cross-origin fetch doesn't receive session cookies.

**Fix:** Changed `API_BASE` to empty string (`""`) to use relative paths, routing through Next.js rewrites which preserve cookies.

```diff
-const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
+const API_BASE = "";
```

## Workaround
Switch to Legacy UI: https://martian-api.zeabur.app/
