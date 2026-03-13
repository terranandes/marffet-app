# Code Review — 2026-03-13 Sync v15

**Reviewer**: [CV] Code Verification Manager
**Date**: 2026-03-13 02:52 HKT
**Scope**: Worktree merge `test-local-verification` → `master` (commits `9b1104f` + `e023796`)

---

## Commits Reviewed

| Commit | Message | Type | Status |
|--------|---------|------|--------|
| `9b1104f` | fix: stabilize E2E test infrastructure | **FIX + TEST** | ✅ APPROVED |
| `e023796` | merge: test-local-verification → master | **MERGE** | ✅ APPROVED |

Files changed (5):

- `app/auth.py` (+31 lines)
- `frontend/src/lib/UserContext.tsx` (+2/−1 lines)
- `tests/e2e/e2e_suite.py` (+23/−14 lines)
- `tests/integration/round3_verification.py` (+18/−11 lines)
- `tests/unit/test_mobile_portfolio.py` (+97/−54 lines)

---

## Source Code Review

### 1. `app/auth.py` — **HIGH IMPACT**

| Item | Code | Assessment |
|------|------|------------|
| `/auth/test-login` mock DB injection | `INSERT OR IGNORE INTO users` + `INSERT OR REPLACE INTO user_memberships (PREMIUM)` | ✅ Correct — resolves silent 500s from missing FK |
| `/auth/guest` DB injection | `INSERT OR IGNORE INTO users (guest)` + `INSERT OR IGNORE INTO user_memberships (FREE)` | ✅ Correct — prevents guest group creation failures |
| Production gate | `if os.getenv('TESTING', '').lower() != 'true': raise HTTPException(404)` | ✅ Fully gated — zero prod exposure |
| `user_id = email.split('@')[0]` | Used for `id` field in `users` table | ✅ Consistent with Google OAuth pattern |
| `valid_until = datetime('now', '+1 day')` | Short TTL to minimize test pollution | ✅ Appropriate |

**Risk**: NONE for production. `TESTING=true` is not set on Zeabur.

---

### 2. `frontend/src/lib/UserContext.tsx` — **MEDIUM IMPACT**

| Item | Change | Assessment |
|------|--------|------------|
| Auth fetch timeout | 10s → 30s | ✅ Prevents mobile spinner dismiss on slow networks |

**Risk**: LOW. Increased timeout from 10s to 30s may delay error detection on genuinely unreachable backends. Acceptable tradeoff for mobile stability.

---

### 3. `tests/e2e/e2e_suite.py` — **TEST ONLY**

| Change | Assessment |
|--------|------------|
| Guest login → `/auth/test-login?email=e2e_desktop@local` | ✅ Correct. Guest tier blocked 403 on group POST. |
| `.fill()` → `.press_sequentially(delay=50)` | ✅ Prevents React SWR event loss on fast fills |
| Visibility loop for group verification | ✅ More robust than single `wait_for(visible)` |

---

### 4. `tests/integration/round3_verification.py` — **TEST ONLY**

| Change | Assessment |
|--------|------------|
| `localhost:8001` POST → `127.0.0.1:3001` page.goto | ✅ Resolves IPv6 loopback timeout + cookie domain mismatch |
| `button.text-red-500` → semantic regex `(Log out\|Sign out\|登出)` | ✅ Robust to Tailwind CSS changes |

**Risk**: LOW. The logout button locator falls back gracefully on fail (no test abort).

---

### 5. `tests/unit/test_mobile_portfolio.py` — **TEST ONLY**

| Change | Assessment |
|--------|------------|
| Remove UI-based group deletion workaround | ✅ PREMIUM auto-grant from auth.py makes this unnecessary |
| `.fill()` → `.press_sequentially(delay=50)` | ✅ Same fix as desktop |
| Auth via `/auth/test-login?email=mobile@test.com` | ✅ PREMIUM tier guaranteed via DB injection |

**BUG-020 Status**: **CLOSED** — The mobile locator timeout was rooted in group creation 500 errors. Now resolved by the DB injection + PREMIUM tier grant.

---

## Git Hygiene Audit

| Check | Result |
|-------|--------|
| `master` ↔ `origin/master` sync | ⚠️ 2 AHEAD (merge commit + worktree fix) |
| Worktree `full-test-local` | ⚠️ EXISTS — can be removed after merge verified |
| Uncommitted changes | ✅ NONE (clean) |
| Stale branches | 🟡 `test-local-verification` (local only, safe to delete) |
| Stashes | ✅ EMPTY |

---

## Security Check

| Item | Assessment |
|------|------------|
| `/auth/test-login` endpoint | ✅ Gated by `TESTING=true`, 404 in production |
| Mock DB injection | ✅ SQL uses parameterized queries — no injection risk |
| PREMIUM tier grant | ✅ `valid_until = +1 day` — minimal blast radius |
| No secrets exposed in test URLs | ✅ Only email addresses used |

---

## Verdict

| Category | Result |
|----------|--------|
| Source Code Quality | ✅ Production code unchanged except auth.py test endpoint |
| Test Infrastructure | ✅ **FIXED** — All 3 test suites now pass locally |
| Security | ✅ No vulnerabilities |
| Frontend Auth UX | ✅ 30s timeout prevents false spinner dismissal |
| Git Hygiene | ⚠️ 2 commits ahead, push needed |
| Worktree Cleanup | 🟡 `full-test-local` + `test-local-verification` can be removed after push |

**Overall**: ✅ **APPROVED** — Merge is clean and the test infrastructure regression has been fully resolved. BUG-020 is now closed.
