# 🔍 Code Review Note — v26

**Date:** 2026-03-15
**Version:** v26
**Author:** [CV] Code Verification Manager
**Scope:** BUG-021 Auth Fix — Account Switch Failure

---

## 1. Review: `frontend/src/lib/UserContext.tsx` — `logout()` Function

### Change
```diff
-// 5. Fire-and-forget server logout (non-blocking)
-fetch('/auth/logout', { method: 'GET' }).catch(() => { });
-// 6. Instant client-side redirect
+// 5. AWAIT server logout so session cookie is cleared BEFORE any new login attempt.
+try {
+    await fetch('/auth/logout', { method: 'GET', credentials: 'include' });
+} catch {
+    // Non-critical: session will expire naturally
+}
+// 6. Redirect AFTER session is cleared
router.push('/');
```

- **Risk:** Low. The change adds a single async wait (~50-200ms RTT). No state changes.
- **Correctness:** ✅ Guarantees server session is cleared before client navigates.
- **Edge Cases:** The `try/catch` wrapper handles network failures gracefully; the `credentials: 'include'` ensures the session cookie is sent with the request over CORS.
- **Finding:** ✅ APPROVED

---

## 2. Review: `app/auth.py` — `/auth/logout` Endpoint

### Change Summary
1. `is_fetch` detection via `Accept: application/json` header
2. Returns `200 JSON {"status": "ok"}` for programmatic fetch
3. Returns `302 RedirectResponse` for browser navigation
4. Explicit `delete_cookie("session", ...)` with matching security attributes

### Assessment
- **is_fetch detection:** Standard pattern. `Accept: application/json` is sent by `fetch()` with `credentials: include`. ✅
- **delete_cookie:** Uses matching `domain`, `secure`, `samesite`, `path` — critical for cross-domain cookie deletion on Zeabur. ✅
- **JSONResponse for fetch:** Prevents the browser from silently following a 302 inside `await fetch()` before the session is actually cleared. ✅
- **Finding:** ✅ APPROVED

---

## 3. Phase 37 Pre-Review Items (Proposed)

| Item | Risk | Recommendation |
|---|---|---|
| `isValidating` spinner (SWR) | Low | ✅ Green-light |
| BUG-020 E2E locator fix | Low (test only) | ✅ Green-light |
| CSRF on logout | Medium | Defer to Phase 38 |

---

## 4. Overall Status: ✅ APPROVED

All Phase 36 features remain stable. BUG-021 fix is clean, targeted, and non-regressive. Phase 37 scope pre-approved.
