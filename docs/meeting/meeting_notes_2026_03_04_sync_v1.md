# Meeting Notes — 2026-03-04 Agents Sync v1
**Date:** 2026-03-04 03:12 HKT
**Attendees:** [PL], [PM], [SPEC], [CODE], [CV], [UI], BOSS (Terran)
**Purpose:** Sort out next steps after chart visualization fixes

---

## Agenda & Status Board

### 1. Live Progress (`tasks.md`)

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 26: Tier Differentiation (Backend) | ✅ COMPLETED | BUG-A/B fixed, committed `b419ea8` |
| **Chart Fix: Comparison X-Axis** | ✅ COMPLETED | Unified year-set, `fd33f1c` |
| **Chart Fix: Comparison Colors** | ✅ COMPLETED | Stock 3 teal→gold, `a0aeb4d` |
| **Data Fix: Pre-IPO/興櫃 Filtering** | ✅ COMPLETED | Gap detection in ROI calculator, `e4d0448` |

### 2. Recent Commits (This Session)

| Commit | Description |
|--------|-------------|
| `e4d0448` | fix(data): filter 興櫃/pre-IPO data via gap detection |
| `b701741` | fix(data): filter out pre-IPO orphan data points |
| `fd33f1c` | fix(compound): align comparison chart X-axis for different IPO dates |
| `f3225df` | docs(jira): BUG-012-CV home page i18n keys displayed raw |
| `a0aeb4d` | fix(ui): comparison chart color distinction — Stock 3 teal→gold |
| `b419ea8` | feat(tier): implement 4-tier backend gating (FREE/PREMIUM/VIP/GM) |

### 3. JIRA Triage

| Ticket | Status | Severity | Notes |
|--------|--------|----------|-------|
| BUG-000 → BUG-009 | CLOSED | — | Previous phases |
| **BUG-010-CV** | 🟡 OPEN (Deferred) | Low | Mobile portfolio card click timeout. Phase F card redesign may fix — needs re-verification. |
| BUG-011-CV | CLOSED | — | Portfolio transaction edit failure |
| **BUG-012-CV** | 🟡 OPEN | Medium | Home page i18n keys raw. Missing `Home.*` keys in locale files. Pre-existing. |
| **Total: 11/13 CLOSED** | | | 2 remain open |

### 4. Git Status

| Item | Status |
|------|--------|
| Branch | `master` — synced with `origin/master` at `e4d0448` |
| Worktrees | ✅ Clean — only main |
| Branches | ✅ Clean — only `master` |
| Stashes | ✅ Clean — none |
| Uncommitted | None (only test evidence PNGs, gitignored) |

### 5. Deployment Completeness

| Check | Result |
|-------|--------|
| `marffet-api.zeabur.app/health` | ✅ `{"status":"healthy","version":"1.0.2"}` |
| `marffet-app.zeabur.app` | ✅ HTTP 200 (pending chart fix deploy verification) |
| Local-vs-Remote | ⚠️ Remote has chart fix + 興櫃 filter deployed, needs E2E verification |
| `terranandes/marffet` (private) | ✅ Synced |
| `terranandes/marffet-app` (public) | ⏳ Content not yet published |

### 6. Performance / Feature Report

**Implemented this session:**
- Comparison mode unified X-axis (all stocks' years merged, null-padded, connectNulls:false)
- Color distinction improvement (Stock 3: teal → gold)
- Pre-IPO rogue data filtering (< 20 trading days)
- 興櫃 gap detection (keep only latest contiguous year block)

**Not yet verified on remote:**
- The 興櫃 filter (`e4d0448`) is pushed but Zeabur may need rebuild for backend changes

---

## [PM] Next Steps — Prioritized Backlog

### 🔴 P0: Immediate (This Session or Next)
1. **BUG-012-CV: Fix Home Page i18n** — Add all `Home.*` keys to `en.json`, `zh-TW.json`, `zh-CN.json`
2. **Full-Test Restart** — Run E2E suite against Zeabur to verify chart fix + 興櫃 filter deployed correctly
3. **Verify 5-Tier Gating E2E** — Test Guest/FREE/PREMIUM/VIP/GM limits on local (API + localStorage)

### 🟡 P1: Near-Term Feature Work
4. **Phase C: AI Copilot Polish** — Blocked on GCP API? Or resolved after `gemini-2.5-flash` update?
5. **Phase D: Notification Trigger System** — Backend engine needed for SMA/Cap/CB alerts
6. **BUG-010-CV: Mobile Portfolio Card** — Re-verify after Phase F card redesign
7. **Accounts-Over-Time Chart** — BOSS requested feature, not started
8. **Public GitHub Showcase** — Push curated code to `terranandes/marffet-app`

### 🟢 P2: Future / Deferred
9. **Google Advertisement Integration** — Not started
10. **Cloud Run Evaluation** — Alternative to Zeabur
11. **Email Support** — Not started
12. **DB Optimization** — Consider read replicas, connection pooling
13. **Grand Correlation v9** — Push match rate beyond 84.71%

---

## [SPEC] Technical Debt & Architecture Notes

- **ROI Calculator** now has gap detection logic — should be documented in `specification.md`
- **Frontend `page.tsx`** has unified X-axis logic inline — could extract to utility function
- **Market Data Provider** returns pre-IPO data from DuckDB — the gap filter is in ROI calculator, not at data source level. Consider data-level cleanup later.

---

## [CODE] Open Items

- `start_app.sh` occasionally fails to spawn `uvicorn` (binary not on PATH when not in venv). Consider adding `uv run` prefix.
- `/api/notifications` returns 500 consistently — endpoint stub exists but no backend engine.
- Multiple `Backup portfolio.db` auto-commits clutter the git log — consider `.gitignore` or separate branch.

---

## [PL] Summary Report to Terran

> **Boss, here's where we stand:**
>
> **Completed this session:**
> - ✅ Comparison chart X-axis alignment (6533 now starts correctly at 2017)
> - ✅ Comparison chart color distinction (Stock 3 now gold)
> - ✅ Pre-IPO/興櫃 data filtering via gap detection
> - ✅ All fixes committed and pushed to origin
>
> **Open bugs:** BUG-010 (mobile, deferred) and BUG-012 (home i18n, pre-existing)
>
> **Recommended next steps (sorted by priority):**
> 1. Fix BUG-012 (Home i18n) — ~15 min effort, high visibility
> 2. Run `@[/full-test]` to verify remote deployment
> 3. E2E test 5-tier gating (BOSS: do you want us to test with real accounts or API-level mock?)
> 4. Decide on Phase C (AI Copilot) vs Phase D (Notifications) vs new features (Accounts chart)
>
> **Git & infra are clean** — single branch, no worktrees, no stashes, Zeabur healthy.

---

## Action Items

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | Fix BUG-012: Add Home.* i18n keys to all 3 locale files | [UI] | HIGH |
| 2 | Run @[/full-test] on Zeabur to verify 興櫃 filter deploy | [CV] | HIGH |
| 3 | E2E test 5-tier gating (Guest→GM) | [CV] | HIGH |
| 4 | Update `specification.md` with gap-detection data filtering rule | [SPEC] | MEDIUM |
| 5 | Decide next feature phase (AI Copilot / Notifications / Accounts Chart) | [PM] + BOSS | MEDIUM |
| 6 | Re-verify BUG-010 mobile card after Phase F redesign | [UI] | LOW |
| 7 | Publish curated code to `terranandes/marffet-app` | [PL] | LOW |

---

**Meeting adjourned at 03:25 HKT.**
