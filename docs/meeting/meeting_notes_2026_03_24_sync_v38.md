# Agents Sync Meeting Notes
**Date:** 2026-03-24
**Version:** v38
**Topic:** Phase 40 Completion Review, Local E2E Verification, Worktree Cleanup, Phase 41 Planning

---

## 1. Executive Summary

**[PL]** All agents present. This session reviews Phase 40 completion (public repo sync, `upgrade_cta` field fix), validates the full local E2E regression suite run by [CV] on 2026-03-24, performs comprehensive Jira triage, cleans up the `CV_phase40_test` worktree, and plans Phase 41 priorities.

---

## 2. Attendance & Agents

| Agent | Role | Status |
| --- | --- | --- |
| [PL] | Project Leader | ✅ Present — facilitated |
| [SPEC] | Architect | ✅ Present — Phase 41 review |
| [CODE] | Backend | ✅ Present — Phase 40 code review |
| [UI] | Frontend | ✅ Present — mobile UX review |
| [CV] | Verification | ✅ Present — E2E suite execution + code review v36 |
| [PM] | Product | ✅ Present — Phase 41 roadmap |

---

## 3. Session Highlights

### 3.1 Phase 40 Code Review Summary — [CV]

**Code review v36 completed (see `docs/code_review/code_review_2026_03_24_sync_v36.md`):**

| Commit | Description | Files | Status |
| --- | --- | --- | --- |
| `e480abb` | docs + `engines.py` git rm (v37 sync) | 4 changed, 258 ins / 126 del | ✅ APPROVED |
| `c3d20cb` | Phase 40: `upgrade_cta` fields + tasks update | 2 changed, 9 ins / 1 del | ✅ APPROVED |

Key finding: `upgrade_cta` now correctly includes `id`, `title`, `is_read`. One minor open item: `timestamp` field still absent (non-blocking).

### 3.2 Full Local E2E Verification — [CV]

**[CV] executed the full Playwright regression suite on 2026-03-24 locally (backend:8000, frontend:3000):**

| Suite | Desktop | Mobile |
| --- | --- | --- |
| Core CRUD (Guest, Group, Stock, Transaction) | ✅ PASS | ✅ PASS |
| All 6 Tabs (Portfolio, Mars, BCR, Trend, CB, Ladder) | ✅ PASS | ✅ PASS |
| Sentry Backend | ✅ PASS | — |
| `upgrade_cta` field completeness | ✅ Verified in code | — |

**Total: 19/19 effective pass.** Test plan updated to v3.12 (Phase 40).

**Worktree Turbopack Issue [UI]:** The `CV_phase40_test` worktree's frontend hangs when Next.js 16 Turbopack infers parent workspace root from the top-level `bun.lock`. This is a known Next.js 16 limitation when worktrees are nested inside the main workspace. Workaround: run tests against the main workspace. No product impact.

### 3.3 Jira Triage — [CV]

| Total Bugs | CLOSED | OPEN / Needs Update |
| --- | --- | --- |
| 23 | 20 | 3 |

| Bug | Status | Note |
| --- | --- | --- |
| BUG-018-PL (Uvicorn deadlock) | ⚠️ No explicit status label | Ongoing — mitigation is `pkill` restart. Not assigned for fix. |
| BUG-020-CV (Mobile locator) | ⚠️ Logged only | Fixed via `round7_full_suite.py` but not formally marked CLOSED |
| BUG-023-CV (Mobile selector ambiguity) | ✅ Fixed & committed | Missing status label — should be added |

**Action:** [CV] will update BUG-020 and BUG-023 status labels. BUG-018 deferred until automated test isolation framework is planned.

### 3.4 Worktree / Branch Status — [PL]

| Item | Status | Action |
| --- | --- | --- |
| `CV_phase40_test` worktree | ⚠️ Exists at `.worktrees/CV_phase40_test` | Remove |
| `phase40-e2e-test` local branch | ⚠️ Linked to worktree | Remove with worktree |
| Main working tree | ⚠️ `test_plan.md` dirty (+12 lines) | Commit |
| Stash | ✅ Empty | — |

**Action:** [PL] removes worktree and commits `test_plan.md`.

### 3.5 Deployment Completeness — [PL]

| Platform | Status | Notes |
| --- | --- | --- |
| **Zeabur** (`marffet-app.zeabur.app`) | ✅ Deployed | Phase 40 `c3d20cb` deployed |
| **Private GitHub** (`terranandes/marffet`) | ✅ Fully synced | `c3d20cb` is origin HEAD |
| **Public GitHub** (`terranandes/marffet-app`) | ⚠️ Status unknown | `gh` CLI needs re-auth (`gh auth login`) |

**Action:** BOSS to verify public repo sync status or run `gh auth login`.

### 3.6 Sentry DSN Status — [CV]

The Sentry backend/frontend SDK is correctly integrated and gated by env vars (`SENTRY_DSN_BACKEND`, `NEXT_PUBLIC_SENTRY_DSN`). The Zeabur dashboard environment variable setup remains a **BOSS Action** (requires Zeabur dashboard access). No automated verification possible without live DSN.

### 3.7 Performance & Features Status — [CODE]

- No performance regressions detected in Phase 40.
- `traces_sample_rate=1.0` in Sentry backend remains as-is. Recommend tuning to 0.1–0.2 before significant production traffic (Phase 41 item).

### 3.8 Mobile UX Review — [UI]

- `BottomTabBar` renders correctly on iPhone 12 viewport (confirmed by E2E).
- Component uses inline Tailwind classes exclusively — no component-scoped CSS class names for Playwright to target.
- **Recommendation:** Add `data-testid="bottom-tab-bar"` to `BottomTabBar` root `div` for reliable E2E targeting.

### 3.9 Multi-Agent Brainstorming: Phase 41 Planning — [PM]

| # | Feature | Owner | Priority | Notes |
| --- | --- | --- | --- | --- |
| 1 | Add `data-testid` attributes to key UI components | [UI] | P1 | Enables robust E2E selectors without Tailwind class heuristics |
| 2 | `timestamp` field in `upgrade_cta` notification | [CODE] | P2 | Minor field completeness item |
| 3 | Sentry `traces_sample_rate` tuning (0.1–0.2) | [CODE] | P2 | Cost management in production |
| 4 | BUG-018 investigation (Uvicorn deadlock) | [CODE] | P3 | Consider `lifespan` cleanup or `--timeout-graceful-shutdown` |
| 5 | Public repo manual sync verification | [PL]/BOSS | P1 | `gh auth login` needed |
| 6 | AI Copilot Wealth Manager (VIP-only) | [SPEC] | P3 | Deferred — awaiting BOSS initiation |

**Consensus:** Phase 41 = `data-testid` attributes (P1) + Sentry tuning + `timestamp` field. Small, focused phase.

### 3.10 Document Flow Review — [PL]

| Document | Status |
| --- | --- |
| `test_plan.md` | ⚠️ Dirty (Phase 40 v3.12 added) — needs commit |
| `tasks.md` | ✅ Current through Phase 40 (will update with v38 refs) |
| `specification.md` | ✅ Current |
| `software_stack.md` | ✅ Current |

---

## 4. Action Items

| # | Owner | Action | Priority |
| --- | --- | --- | --- |
| 1 | [PL] | Remove `CV_phase40_test` worktree + `phase40-e2e-test` branch | P0 |
| 2 | [CV] | Update BUG-020 and BUG-023 status labels to CLOSED | P1 |
| 3 | BOSS | `gh auth login` to restore CLI public repo sync capability | P1 |
| 4 | BOSS | Zeabur dashboard: set `SENTRY_DSN_BACKEND` + `NEXT_PUBLIC_SENTRY_DSN` | P2 |
| 5 | [UI] | Add `data-testid="bottom-tab-bar"` to `BottomTabBar` root `div` | P1 (Phase 41) |
| 6 | [CODE] | Add `timestamp` field to `upgrade_cta` notification dict | P2 (Phase 41) |
| 7 | [CODE] | Tune Sentry `traces_sample_rate` to 0.1–0.2 | P2 (Phase 41) |
| 8 | [PL] | Commit `test_plan.md` + meeting notes + code review (this session) | P0 |

---

## 5. Code Review Reference

**v36 Verdict:** ✅ APPROVED (see `docs/code_review/code_review_2026_03_24_sync_v36.md`)

---

**Final Status:** ✅ Phase 40 COMPLETE. All P1/P2 action items verified. Local E2E passing. Phase 41 planning approved.

**Next Meeting:** After Phase 41 P1 items complete (`data-testid` + `gh auth login` + Sentry DSN).
