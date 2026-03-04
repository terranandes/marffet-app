# Meeting Notes — 2026-03-04 Agents Sync v2
**Date:** 2026-03-04 15:35 HKT
**Attendees:** [PL], [PM], [SPEC], [CODE], [CV], [UI], BOSS (Terran)
**Purpose:** Sync-up after Public Repo Promotion & Documentation Updates

---

## Agenda & Status Board

### 1. Live Progress (`tasks.md`)

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 26: Tier Differentiation | ✅ COMPLETED | BUG-A/B fixed `b419ea8` |
| Phase 27: Chart Fixes | ✅ COMPLETED | X-axis unified, pre-IPO filtered `e4d0448` |
| **Phase 28: Public Repo Showcase** | ✅ COMPLETED | Live at `terranandes/marffet-app` `46e08c7` |
| **Document Flow Update** | ✅ COMPLETED | `marffet_showcase_github.md` created, rules synced |

### 2. Recent Commits (This Session)

| Commit | Description |
|--------|-------------|
| `46e08c7` | feat: initial public showcase — README (EN/TW/CN) + screenshots + LICENSE (Public Repo) |
| `496964f` | docs: sync README tier tables with spec v5.0 + public repo plan (Private Repo) |
| (Pending) | docs: update tasks.md, marffet_showcase_github.md, and sync v2 notes |

### 3. JIRA Triage

| Ticket | Status | Severity | Notes |
|--------|--------|----------|-------|
| BUG-000 → BUG-009 | CLOSED | — | Previous phases |
| BUG-011-CV | CLOSED | — | Portfolio transaction edit failure |
| **BUG-010-CV** | 🟡 OPEN (Deferred) | Low | Mobile portfolio card click timeout |
| **BUG-012-CV** | 🟡 OPEN | Medium | Home page i18n keys raw. Missing `Home.*` keys in locale files. |
| **Total: 11/13 CLOSED** | | | 2 remain open |

### 4. Git Status

| Item | Status |
|------|--------|
| Branch | `master` — clean and synced |
| Worktrees | ✅ Clean — only main |
| Stashes | ✅ Clean — none |

### 5. Deployment Completeness

| Check | Result |
|-------|--------|
| `marffet-api.zeabur.app/health` | ✅ `{"status":"healthy","version":"1.0.2"}` |
| `marffet-app.zeabur.app` | ✅ Live |
| Local-vs-Remote | ⚠️ Remote has BUG-012. Needs E2E validation after next deploy. |
| `terranandes/marffet` (private) | ✅ Up to date with docs |
| `terranandes/marffet-app` (public) | ✅ Published and verified! (Needs BOSS to set About/Topics) |

### 6. Code Review Notes
Reviewing the public repo changes and documentation sanitization.
- **Security Check:** Zero leaks of `andes` or `moneycome` within public prose (`marffet_showcase_github.md`).
- **Integrity Check:** All 3 READMEs (EN, TW, CN) perfectly match the `specification.md` 5-tier matrix.
- `document-flow.toml` successfully orchestrated updating across READMEs and generating the showcase doc.

---

## [PM] Next Steps — Prioritized Backlog

### 🔴 P0: Immediate (This Session or Next)
1. **GitHub Settings (BOSS):** Set description, website, and topics for the public repo `terranandes/marffet-app`.
2. **BUG-012-CV: Fix Home Page i18n** — Add all `Home.*` keys to locale JSONs (`en`, `zh-TW`, `zh-CN`).
3. **Full-Test Restart** — Run E2E suite against Zeabur to verify chart fix + pre-IPO filter deployed correctly.

### 🟡 P1: Near-Term Feature Work
4. **Phase C: AI Copilot Polish** / **Phase D: Notification Trigger System**
5. **Accounts-Over-Time Chart** — Multi-portfolio net-worth tracking requested by BOSS.

---

## [PL] Summary Report to Terran

> **Boss, here's the v2 sync update:**
>
> **Completed this session:**
> - ✅ Executed the Public Repo Promotion Plan. `terranandes/marffet-app` is live with 3 languages and polished dark-mode screenshots.
> - ✅ Created `marffet_showcase_github.md` strictly adhering to the new sensitive words policy (zero leaks verified via grep).
> - ✅ Updated `tasks.md` to reflect Phase 28 completion.
>
> **Pending your action:**
> - Please update the GitHub `About` section for the public repo (instructions are in `marffet_showcase_github.md`).
>
> **What's Next for Us:**
> We have 2 open bugs. **BUG-012 (i18n keys showing raw)** is highly visible on the Home Page and needs a quick fix. After that, we should run `@[/full-test]` to ensure all recent backend chart/filter fixes are alive and stable on Zeabur.
>
> Shall we proceed with fixing BUG-012 now?

---

**Meeting adjourned at 15:35 HKT.**
