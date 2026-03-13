# AntiGravity Agents Sync-Up Meeting

**Date**: 2026-03-13 14:15 HKT
**Version**: v16
**Lead**: [PL] Project Leader
**Attendees**: [PM], [SPEC], [PL], [CODE], [UI], [CV]

---

## 1. Project Live Progress

| Phase | Status | Summary |
|-------|--------|---------|
| Phase 34 | ✅ COMPLETED | Auth UX, Strict AuthGuard, Elegant Logout |
| Phase 35 | 🟡 IN PROGRESS | Rounds 1–3 ✅ · Round 4 Guest Mode ❌ FAILED |

- HEAD: `2 commits ahead` of `origin/master`.
- Working tree: Uncommitted files related to Guest Mode Architecture Brainstorming and markdown lint fixes.
- Zeabur deployment: **LIVE** (HTTP 200).

---

## 2. Key Findings Since v15

### ❌ E2E Guest Login Round 4 Fails - Core Architecture Bug

In v15, we celebrated `e2e_suite.py` passing, but that was because Hotfix 35.9 explicitly mocked the guest flow by redirecting it to a fully-authenticated test user (`/auth/test-login?email=e2e_desktop@local`).

When BOSS requested to **"Run round 4 with guest mode again"**, [PL] reverted the test to actually test the `/auth/guest` endpoint.

**Result:** The test consistently times out when waiting for the new group tab to appear.

**Root Cause Analysis:**
[PL] and [CV] conducted a deep dive and found a massive disconnect in the Guest Mode Architecture:

1. **The Dual Guest Architecture:**
   - There is a `GuestPortfolioService` (LocalStorage) that is *supposed* to be used for guest storage.
   - However, clicking "Explore as Guest" calls `POST /auth/guest`, which generates a **REAL SQLite backend session** for user `guest@local`.
   - Because the user now has a valid session, `usePortfolioData.ts` receives a `200 OK` and selects the `ApiPortfolioService` (Backend), completely bypassing LocalStorage.

2. **The Fails:**
   - **Silent 500 API errors:** The guest user hits the Backend API to create groups. Even with DB cleanup and `PREMIUM` tier injection, the API calls fail silently to trigger the SWR revalidation of `mutateGroups()`.
   - **Data Pollution:** Since *all* guest users share the `user_id='guest'` in SQLite, this is not an isolated guest mode, but a shared public account.
   - **UX Trust Violation:** The UI says "Data stored locally only", but it actually sends everything to the backend SQLite DB.

**Resolution Generated:**

- Created `docs/brainstorming/guest_mode_architecture_analysis.md` outlining the problem.
- Conducted `docs/brainstorming/guest_mode_multi_agent_review.md` providing 3 architectural paths forward.

### ✅ Formatting Fixes

- Fixed `MD022/blanks-around-headings` in `docs/product/BOSS_TBD.md` by wrapping all markdown headings in blank lines.

---

## 3. Bug Triage & JIRA Reconciliation

| Bug ID | Title | Status | Notes |
|--------|-------|--------|-------|
| BUG-021-CV | Guest Mode uses Shared Backend DB instead of LocalStorage | 🔴 CRITICAL | Root cause of Round 4 failures |
| BUG-017-CV | Remote E2E Add Stock Timeout | ⚠️ OPEN | Zeabur cold start |
| BUG-018-PL | Backend DB Deadlock on Reload | ⚠️ OPEN | Dev hot-reload only |
| BUG-000-CV | Local Worktree Frontend .env.local | 🟡 LOW | Non-blocking |

---

## 4. Code Review Summary

> See: `docs/code_review/code_review_2026_03_13_sync_v16.md`

**[CV] Verdict**: 🟡 **CHANGES REQUESTED** — The test scripts were correctly reverted to test the true Guest Flow, which properly identified the architectural bug. However, the application code itself requires a significant fix to the `PortfolioService` routing to resolve the Guest Mode architecture completely.

---

## 5. Multi-Agent Brainstorming: Guest Mode Overhaul

**[PM] — Product Strategy:**
> "Explore as Guest" explicitly states "Data stored locally only". Right now we are violating that promise. We must fix this to use LocalStorage.

**[SPEC] — Architecture:**
> `usePortfolioData.ts` needs a strict rewrite: if `user.is_guest === true`, it MUST select `GuestPortfolioService` regardless of backend API reachability. Also, `/auth/guest` should not issue a persistent backend cookie.

**[CODE] — Backend & Frontend:**
> We can remove the SQLite inserts in `auth.py` for `/auth/guest`. On the frontend, `Sidebar.tsx` sets a React context flag, and `usePortfolioData.ts` reads that flag to route to LocalStorage.

**[CV] — Quality:**
> We cannot proceed with E2E Round 4 (Guest Mode) until the overarching architecture correctly routes guest data to LocalStorage. The current test fails precisely because of this backend-routing limitation.

**Decision Log:**

| Decision | Rationale |
|----------|-----------|
| Halted E2E Round 4 for Guest | Fails due to application logic, not test logic |
| Recommended Path: Option C | Switch Guest Mode completely to LocalStorage to match UX promises and fix test stability |
| MD022 Linter Fixed | Cleaned up `BOSS_TBD.md` line spacing |

---

## 6. Action Items

| Priority | Agent | Action |
|----------|-------|--------|
| 🔴 HIGH | [PL/CODE] | Refactor `usePortfolioData.ts` and `auth.py` to route Guest Mode via LocalStorage |
| 🔴 HIGH | BOSS | Review `guest_mode_architecture_analysis.md` and confirm the proposed "Option C" Path |
| 🟡 MED | [CV] | Re-run `e2e_suite.py` for Guest Mode after the LocalStorage refactor |

---

## 7. [PL] Summary to Terran

Terran, here is your Sync Summary (v16):

1. **Guest Mode Test Failed (As Expected):** When I reverted the E2E script back to testing the true Guest Mode, it failed. This led to a major discovery about the app's architecture.
2. **The Guest Mode Bug:** Guest mode currently uses the **backend SQLite DB** instead of LocalStorage. This means all "guests" share the same data, and it violates the "Data stored locally only" text in the UI.
3. **Brainstorming:** I conducted a full multi-agent review of this issue (`docs/brainstorming/guest_mode_multi_agent_review.md`). The agents strong recommend switching Guest Mode to use LocalStorage strictly.
4. **Linter Fixes:** I fixed the `MD022` formatting error in `BOSS_TBD.md`.
5. **Next Steps:** We need your approval to implement the LocalStorage fix for Guest Mode. Once that is done, E2E Round 4 will pass.

I am committing these findings and notes now.
