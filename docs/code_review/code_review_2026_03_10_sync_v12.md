# Code Review — 2026-03-10 Sync v12
**Reviewer**: [CV] Code Verification Manager
**Date**: 2026-03-10 00:51 HKT
**Scope**: 6 commits since v11 meeting (`0563290..b1d8746`)

---

## Commits Reviewed

| Commit | Message | Type | Status |
|--------|---------|------|--------|
| `786b040` | chore: prune 66 pre-March meeting/code-review files, collapse tasks.md | Housekeeping | ✅ OK |
| `508c4a8` | chore: relocate Remaining Open Items below collapsed phases | Docs | ✅ OK |
| `6a0716a` | chore: complete Phase 35 Round 2 verification | Test Script | ✅ OK |
| `9a1a15b` | chore: add tests/evidence to gitignore | Config | ✅ OK |
| `dd995de` | fix(auth): prevent infinite mobile spinner by applying timeout | **SOURCE** | ✅ APPROVED |
| `b1d8746` | fix(auth): align login redirect URI with callback | **SOURCE** | ✅ APPROVED |

---

## Source Code Review

### 1. `frontend/src/lib/UserContext.tsx` (commit `dd995de`)

**Changes**: +7 / −6 lines

| Item | Assessment |
|------|-----------|
| Timeout moved outside try/catch | ✅ Correct — ensures AbortController fires even if try block hangs before `clearTimeout` |
| `clearTimeout(timeoutId)` in finally | ✅ Proper cleanup — prevents timer leak on normal completion |
| Timeout reduced 15s → 10s | ✅ Acceptable — 10s is generous for `/auth/me` + `/api/notifications` |
| `console.warn` for notification failures | ✅ Good — visibility for debugging without crashing the app |
| Error naming (`notifErr`) | ✅ Better than anonymous catch |

**Risk**: NONE. Change is additive and backwards-compatible.

### 2. `app/auth.py` (commit `b1d8746`)

**Changes**: +28 / −39 lines (net −11 lines = simplification)

| Item | Assessment |
|------|-----------|
| Removed Referer-based redirect_uri computation | ✅ Correct — eliminates the source of OAuth mismatch |
| `FRONTEND_URL`-based deterministic logic | ✅ Matches `/auth/callback` logic exactly |
| Removed broken `database.connection` import in guest mock | ✅ Correct — module didn't exist; was causing 500 errors |
| Guest mock returns `terranfund@gmail.com` | ⚠️ **WARNING**: Must be reverted before production deploy |
| Fallback to `request.url_for` if FRONTEND_URL is `/` | ✅ Correct — handles local dev without env var |

**Risk**: LOW. The auth logic simplification is sound. The only concern is the active guest mock which bypasses real authentication.

---

## Git Hygiene Audit

| Check | Result |
|-------|--------|
| `master` ↔ `origin/master` sync | ✅ SYNCED (`b1d8746`) |
| Uncommitted changes | ⚠️ 2 FILES (`portfolio.db`, `BOSS_TBD.md`) |
| Stale branches | ✅ NONE (only `master`) |
| Stale worktrees | ✅ NONE |
| Stashes | ✅ EMPTY |

---

## Security Check

| Item | Assessment |
|------|-----------|
| OAuth redirect_uri fix | ✅ Improves security — prevents mismatch exploitation |
| Guest mock endpoint | ⚠️ Returns authenticated session without Google OAuth — OK for local testing, **MUST REVERT for production** |
| UserContext timeout | ✅ No security impact — timing change only |
| No secrets exposed | ✅ Confirmed |

---

## Verdict

| Category | Result |
|----------|--------|
| Source Code Quality | ✅ Both fixes are correct and well-scoped |
| Git Hygiene | ✅ Synced, clean branches/worktrees |
| Security | ⚠️ Guest mock needs revert pre-deploy |
| Deployment Readiness | 🟡 Zeabur stale — needs redeploy + mock revert |

**Overall**: ✅ **APPROVED** — 2 source changes verified correct. Housekeeping commits clean. One action item: revert guest mock before production deployment.
