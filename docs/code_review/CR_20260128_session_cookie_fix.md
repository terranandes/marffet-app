# Code Review: Session Cookie Architecture Fix
**Date:** 2026-01-28
**Reviewer:** [CV] Code Verification Agent
**Scope:** OAuth session handling, cross-domain cookie issues

---

## Summary

Tonight's session revealed a **systemic architectural issue** in how the Next.js frontend makes API calls. Multiple files were inconsistently using either relative paths (correct) or absolute paths with `NEXT_PUBLIC_API_URL` (broken on Zeabur).

## Issue Pattern

```typescript
// ❌ BROKEN: Bypasses Next.js proxy, cross-origin request loses cookies
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
fetch(`${API_BASE}/api/portfolio/groups`, { credentials: "include" });

// ✅ CORRECT: Uses Next.js rewrite proxy, same-origin preserves cookies  
const API_BASE = "";
fetch(`${API_BASE}/api/portfolio/groups`, { credentials: "include" });
```

## Root Cause Analysis

On Zeabur deployment:
- `martian-app.zeabur.app` (Next.js frontend)
- `martian-api.zeabur.app` (FastAPI backend)

These are **different origins**. When frontend fetches `https://martian-api.zeabur.app/api/...`:
1. Browser sees cross-origin request
2. Cookie with `Domain=martian-app.zeabur.app` is NOT sent to `martian-api.zeabur.app`
3. Backend sees no session → returns 401/403 or empty data

Solution: Use Next.js `rewrites` in `next.config.ts`:
```typescript
rewrites() {
  return [
    { source: "/api/:path*", destination: `${API_URL}/api/:path*` }
  ];
}
```
This makes `/api/` requests appear same-origin to the browser, so cookies are sent.

## Files Reviewed & Fixed

| File | Issue | Fix Applied |
|------|-------|-------------|
| `portfolio/page.tsx` | Used `NEXT_PUBLIC_API_URL` | Changed to `""` |
| `admin/page.tsx` | Used `NEXT_PUBLIC_API_URL` | Changed to `""` |
| `race/page.tsx` | Used `NEXT_PUBLIC_API_URL` | Changed to `""` |
| `viz/page.tsx` | Used `NEXT_PUBLIC_API_URL` | Changed to `""` |
| `cb/page.tsx` | Used `NEXT_PUBLIC_API_URL` | Changed to `""` |
| `trend/page.tsx` | Used `NEXT_PUBLIC_API_URL` | Changed to `""` |
| `ladder/page.tsx` | Used `NEXT_PUBLIC_API_URL` | Changed to `""` |
| `mars/page.tsx` | Used `NEXT_PUBLIC_API_URL` | Changed to `""` |
| `myrace/page.tsx` | Used `NEXT_PUBLIC_API_URL` | Changed to `""` |
| `SettingsModal.tsx` | Used `NEXT_PUBLIC_API_URL` | Changed to `""` |
| `AICopilot.tsx` | Used `NEXT_PUBLIC_API_URL` | Changed to `""` |
| `ClientProviders.tsx` | Used `NEXT_PUBLIC_API_URL` | Changed to `""` |

## Backend Fix

```python
# auth.py line 334: Email case sensitivity bug
# BEFORE
is_admin = user.get('email') in GM_EMAILS

# AFTER  
is_admin = user.get('email', '').strip().lower() in GM_EMAILS
```

`GM_EMAILS` stores lowercase emails. If Google returns `Terranandes@gmail.com` (capitalized), the comparison failed.

## Security Considerations

✅ **No security regression.** Using relative paths with Next.js proxy is the recommended pattern for:
- Session-based authentication
- Cross-domain deployments
- Cookie security (SameSite, Secure flags)

## Recommendations

1. **Enforce consistency:** Create a shared constant or context for `API_BASE`
2. **Code pattern:** Consider a custom hook `useApi()` that always uses relative paths
3. **CI check:** Add lint rule to detect `NEXT_PUBLIC_API_URL` usage in fetch calls

## Test Coverage

- [x] Cookie persistence test (curl)
- [x] Session state across redirects
- [ ] Full E2E with Playwright (BUG-007 timeout issue)
- [ ] Mobile Safari (Pending BOSS test)

---
*Review complete. Changes shipped in commit `9f00073`.*
