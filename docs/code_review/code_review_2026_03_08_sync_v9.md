# Code Review — 2026-03-08 Sync v9
**Reviewer**: [CV] Code Verification Manager
**Date**: 2026-03-08 23:07 HKT
**Scope**: Hotfix 35.1 — Convertible Bond Tab Guest Crash Fix

---

## Commits Reviewed

| Commit | Message | Files |
|--------|---------|-------|
| UNSTAGED | Fix CB tab crash: use global fetcher + Array.isArray guard | `frontend/src/app/cb/page.tsx` |

---

## Code Audit: CB Page SWR Fetcher Fix

**[CODE] Root Cause Analysis:**
- The `useSWR` hook in `cb/page.tsx` used an inline fetcher: `(url) => fetch(url, ...).then(res => res.json())`
- When `/api/cb/my_cbs` returned HTTP 404 (guest users have no CB endpoint), `res.json()` still parsed the error response body (a JSON object, not an array).
- SWR treated this as valid data, setting `portfolioCBs` to a non-array object.
- Line 109: `portfolioCBs.map(...)` then threw `TypeError: portfolioCBs.map is not a function`.

**[CODE] Fix Applied:**
```diff
-    const { data: portfolioCBs = [], isValidating: loadingPortfolio } = useSWR<CBData[]>(
+    const { data = [], isValidating: loadingPortfolio } = useSWR<CBData[]>(
         user ? "/api/cb/my_cbs" : null,
-        (url: string) => fetch(url, { credentials: "include" }).then((res) => res.json())
-    );
+        fetcher
+    );
+    const portfolioCBs = Array.isArray(data) ? data : [];
```

**[CV] Analysis:**
1. ✅ The global `fetcher` (L24-27) correctly throws on non-200 responses (`if (!res.ok) throw new Error("Fetch failed")`), so SWR treats the error as an error state, not data.
2. ✅ The `Array.isArray()` guard is a defensive belt-and-suspenders approach — even if SWR somehow provides non-array data, the UI won't crash.
3. ✅ No other tabs share this inline fetcher pattern — all other SWR usage in the codebase already uses the global `fetcher`.

---

## Untracked File / Git Status Audit

| File | Status | Recommendation |
|------|--------|---------------|
| `frontend/src/app/cb/page.tsx` | Modified | Stage and commit (Hotfix 35.1) |
| `app/portfolio.db` | Modified | Normal DB mutation from guest login; `.gitignore` should handle |
| `tests/evidence/*.png` (27 files) | Untracked | Add to `.gitignore` or commit as evidence archive |

---

## Security Check

- No new security concerns. The fix is purely defensive data-type validation.
- The global `fetcher` already includes `credentials: "include"` for cookie auth.

---

## Verdict

| Category | Result |
|----------|--------|
| Source Code (CB Hotfix) | ✅ CORRECT — Minimal surgical fix |
| Regression Risk | ✅ NONE — Only affected CB tab guest path |
| Architecture | ✅ CONSISTENT — Now uses global fetcher like all other tabs |
| Evidence Files | 🟡 27 screenshots in `tests/evidence/` — recommend `.gitignore` |

**Overall**: ✅ **APPROVED** — Commit the hotfix, add evidence to `.gitignore`, and push.
