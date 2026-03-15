# BUG-022-SPEC: Frontend auth hook permanently falls back to Guest Mode without retry

**Reporter:** [SPEC] AntiGravity
**Severity:** High
**Status:** In Progress
**Found During:** Phase 35 Round 7 Full Feature Verification Campaign

## Summary

When the backend API is temporarily unreachable (e.g., cold-start, HTTP/2 protocol errors), both `UserContext.fetchUser` and `usePortfolioData.initService` catch the network error and permanently fall back to Guest Mode / null user **without any retry logic**. Once the API recovers, the user is stuck on the "Authentication Required" lock screen.

## Reproduction

1. Deploy to Zeabur and restart both frontend + backend
2. Navigate to any authenticated page (e.g., `/portfolio`, `/mars`)
3. The initial `/auth/me` fetch fails with `ERR_HTTP2_PROTOCOL_ERROR`
4. Console shows: `API Unreachable, using Guest Mode`
5. User sees 🔒 "Authentication Required" screen permanently
6. Even after backend recovers, the lock screen persists (no retry)

## Root Cause

### Layer 1: `UserContext.tsx` (lines 161-165)
```typescript
catch (e) {
    console.error("Auth check failed:", e);
    setUser(null); // ← No retry, user stays null
}
```

### Layer 2: `usePortfolioData.ts` (lines 41-54)
```typescript
catch (e) {
    console.log("API Unreachable, using Guest Mode");
    setService(PortfolioFactory.getService(false)); // ← Permanent guest
    setIsGuest(true); // ← No retry, [] deps = runs once
}
```

### Layer 3: `AuthGuard.tsx` (line 24)
```typescript
if (!user && !isPublicPage) {
    return <LockScreen />; // ← Blocks all content when user is null
}
```

## Evidence

- Sidebar eventually shows "Admin Dashboard" + "Access Copilot" (session IS valid)
- But page-level auth gates never recover
- `page.evaluate(fetch('/auth/me'))` returns valid TerranFund GM data
- `curl` with same cookie returns 200 OK

## Fix

Add retry with exponential backoff (3 attempts, 1s → 2s → 4s) to:
1. `UserContext.fetchUser` — retry `/auth/me` before giving up
2. `usePortfolioData.initService` — retry auth check before falling back to Guest
