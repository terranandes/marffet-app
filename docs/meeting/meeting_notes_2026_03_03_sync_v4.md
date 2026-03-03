# Meeting Notes — 2026-03-03 Agents Sync v4
**Date:** 2026-03-03 22:27 HKT
**Attendees:** [PL], [PM], [SPEC], [CODE], [CV], [UI], BOSS (Terran)

---

## Agenda & Status Board

### 1. Live Progress (`tasks.md`)

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 25: Marffet Rebrand & Tier Gating | ✅ COMPLETED | Rebrand + docs all done (v3 meeting) |
| Phase 24: VIP/PREMIUM Injection & Sponsorship | ✅ COMPLETED | Backend + Frontend + i18n |
| Phase 23: UI/UX Polish | ✅ Phase A-F COMPLETED | BUG-010 deferred |
| **Phase 26: Tier Differentiation (Backend)** | 🔴 **IN PROGRESS — BROKEN** | 4 files modified, 2 critical bugs found |

### 2. Uncommitted Tier Differentiation Changes (From Prior Session)

**4 files modified, not yet committed:**

| File | Change Summary | Status |
|------|----------------|--------|
| `app/auth.py` | Extracted `get_user_tier_by_email()` helper, refactored `/me` endpoint | 🔴 **CRITICAL BUG** |
| `app/config.py` | Added VIP/GM tier limits | ✅ Correct |
| `app/services/portfolio_service.py` | 4-tier limit enforcement for groups/targets/tx | 🔴 **CRITICAL BUG** |
| `docs/product/specification.md` | Differentiated VIP vs PREMIUM in tier matrix | ✅ Correct |

#### Config Limits Verification (✅ PASS)
| Resource | FREE | PREMIUM | VIP | GM |
|----------|------|---------|-----|-----|
| Groups | 11 | 20 | 30 | 1000 |
| Targets/Group | 50 | 100 | 200 | 1000 |
| Transactions/Target | 100 | 500 | 1,000 | 10,000 |

### 3. Code Review Results

**Verdict: 🔴 FAIL — 2 Critical Bugs Must Be Fixed Before Commit**

Full details: `docs/code_review/code_review_2026_03_03_sync_v3.md`

#### BUG-A: `auth.py` — Duplicate `get_me` Route + Misplaced Helper

- **Lines 296-313**: Old `get_me` function body was NOT fully removed. It fetches `db_profile` then falls into the `get_user_tier_by_email` function definition — this is a **function defined inside another function's `with` block**.
- **Lines 314-356**: `get_user_tier_by_email` is syntactically valid but **wrong indentation level** — it's nested inside the old `get_me`, making it a local function, NOT a module-level function.
- **Lines 359-396**: New `get_me` function — this is the correct one, but it's the **second** `@router.get("/me")` registration. FastAPI will use the **last** registered route, so it might work by accident, but the code structure is wrong.
- **Impact**: At runtime, `get_user_tier_by_email` is a local function inside old `get_me`. When `portfolio_service.py` does `from app.auth import get_user_tier_by_email`, it will **FAIL** with `ImportError` because Python cannot import a nested function.

#### BUG-B: `portfolio_service.py` — Missing Module-Level Imports

- **Lines 6-10**: The edit replaced the original import block but **dropped** two critical import lines:
  ```python
  from app.repositories import user_repo, group_repo, target_repo, transaction_repo
  from app.services import market_data_service, calculation_service
  ```
- These 5 modules (`user_repo`, `group_repo`, `target_repo`, `transaction_repo`, `market_data_service`, `calculation_service`) are used throughout the entire file (31 references).
- **Impact**: Any portfolio operation (create group, add target, add transaction, list groups, etc.) will **crash with `NameError`** at runtime.

### 4. Git Status

| Item | Status |
|------|--------|
| Branch | `master` — **1 commit ahead** of `origin/master` |
| HEAD | `553f8b5` (docs: 5-tier formalization) |
| Origin | `f0e0921` (mark public repo complete) |
| Worktrees | ✅ Clean — only main |
| Branches | ✅ Clean — only `master` + `origin/master` |
| Stashes | ✅ Clean — none |
| Uncommitted | **4 files (auth.py, config.py, portfolio_service.py, specification.md)** |
| Untracked | 5 test evidence PNGs (gitignored) |

### 5. JIRA Triage

| Ticket | Status | Notes |
|--------|--------|-------|
| BUG-000 through BUG-009 | CLOSED | Previous phases |
| BUG-010 | OPEN (Deferred) | Mobile portfolio card click timeout |
| BUG-011 | CLOSED | Portfolio transaction edit failure |
| **Total: 11/12 CLOSED** | | No new tickets filed this session |

### 6. Deployment Completeness

| Check | Result |
|-------|--------|
| `marffet-app.zeabur.app` | ✅ HTTP 200 |
| `marffet-api.zeabur.app/health` | ✅ `{"status":"healthy","service":"marffet-backend","version":"1.0.2"}` |
| Local-vs-Remote discrepancy | ⚠️ Local has uncommitted broken tier code; remote is stable |
| `terranandes/marffet` (private) | ✅ 1 commit ahead |
| `terranandes/marffet-app` (public) | ✅ Created (BOSS) |

### 7. BOSS_TBD Status Check

| Item | Status |
|------|--------|
| ✅ Multi-language | Completed (Phase 22) |
| ✅ Buy-me-coffee buttons | Completed (Phase 24) |
| ✅ Rename Martian to Marffet | Completed (Phase 25) |
| ✅ Rename private repo | Completed by BOSS |
| ✅ Create public repo | Completed by BOSS |
| ✅ Rename Zeabur services | Completed by BOSS |
| ✅ Define 5-tier model | Formalized in v3 session |
| ⏳ Implement tier differentiation (backend) | **IN PROGRESS — BLOCKED (2 bugs)** |
| ⏳ Publish to GitHub (public showcase) | Pending BOSS |
| ⏳ Accounts-over-time chart | Not started |
| ⏳ AICopilot enhancement | Not started |
| ⏳ Google advertisement | Not started |
| ⏳ Cloud Run evaluation | Not started |
| ⏳ Email support | Not started |

### 8. Document-Flow

No document updates needed this session — all 10 product docs were updated in v3 meeting. The `specification.md` diff only adjusts the tier matrix numbers (PREMIUM vs VIP differentiation) which is consistent with the formalized 5-tier model.

### 9. Worktree / Branch / Stash Cleanup

**Already clean from v3 meeting.** No action needed.

---

## [PL] Summary Report to Terran

> **Boss, the tier differentiation implementation from the earlier session has two critical bugs that must be fixed before committing:**
>
> **BUG-A: `auth.py`** — The `get_user_tier_by_email()` helper function was incorrectly placed inside the old `get_me()` function body instead of at module level. This creates a duplicate route AND makes the function un-importable by `portfolio_service.py`.
>
> **BUG-B: `portfolio_service.py`** — Two import lines were accidentally deleted (`from app.repositories import ...` and `from app.services import ...`), removing 5 critical module references. Every portfolio operation will crash.
>
> **The config limits (`config.py`) and specification doc changes are correct and match the approved tier matrix.** The bugs are purely structural — the logic is sound, just the code placement is broken.
>
> **Recommendation:** Fix both bugs (move `get_user_tier_by_email` to module level, delete old `get_me`, restore imports), then re-run verification before committing.
>
> **Deployment is stable** — Zeabur is running the clean code from before this session. These bugs are local-only.

---

## Action Items

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | Fix BUG-A: Move `get_user_tier_by_email` to module level, remove duplicate `get_me` in `auth.py` | [CODE] | **CRITICAL** |
| 2 | Fix BUG-B: Restore missing imports in `portfolio_service.py` | [CODE] | **CRITICAL** |
| 3 | Re-verify locally after fixes (all portfolio CRUD operations) | [CV] | HIGH |
| 4 | Commit + push tier differentiation to origin/master | [PL] | HIGH |
| 5 | Investigate BUG-010 (mobile portfolio card click) | [UI] | Low |

---

**Meeting adjourned at 22:30 HKT.**
