# Meeting Notes — 2026-03-05 Agents Sync v1
**Date:** 2026-03-05
**Attendees:** [PL], [PM], [SPEC], [CODE], [CV], [UI], BOSS (Terran)
**Purpose:** Sync-up after BUG-012 resolution, Playwright remote testing, and Public Repo (`marffet-app`) corrections.

---

## Agenda & Status Board

### 1. Live Progress (`tasks.md`)

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 26: Tier Differentiation | ✅ COMPLETED | BUG-A/B fixed |
| Phase 27: Chart & Data Fixes | ✅ COMPLETED | BUG-012 (i18n raw keys) completely fixed |
| **Phase 28: Public Repo Showcase** | ✅ COMPLETED | Remote E2E verified; Image assets and End-User READMEs deployed |

### 2. Recent Commits

| Commit | Description |
|--------|-------------|
| `8f2e8ec` | docs: integrate Ko-fi and BuyMeACoffee image badges (Private Repo) |
| `15cced3` | docs: use product README for showcase root and resize badges (Public Repo `.marffet-app`) |
| (Pending) | docs: agents-sync-meeting v1 2026-03-05 notes |

### 3. JIRA Triage

| Ticket | Status | Severity | Notes |
|--------|--------|----------|-------|
| **BUG-012-CV** | ✅ CLOSED | Medium | The raw `Home.*` keys in the Hero section are now properly translated across the locale files. Verified with Playwright MCP. |
| **BUG-010-CV** | 🟡 OPEN (Deferred) | Low | Mobile portfolio card click timeout |
| **Total: 12/13 CLOSED** | | | Only 1 deferred bug remains |

### 4. Git Status

| Item | Status |
|------|--------|
| Branch | `master` — clean and synced |
| Worktrees | ✅ Cleaned — `.worktrees/full-test-local` was successfully wiped. |
| Stashes | ✅ Clean — none |

### 5. Deployment Completeness

| Check | Result |
|-------|--------|
| `marffet-api.zeabur.app/health` | ✅ Live and Stable |
| `marffet-app.zeabur.app` | ✅ Live and BUG-012 is visibly fixed |
| Local-vs-Remote | ✅ Passing consistently. The over-aggressive wait-states in Playwright tests were patched. |
| `terranandes/marffet` (private) | ✅ Up to date |
| `terranandes/marffet-app` (public) | ✅ Layout Fixed! Replaced technical README with English End-User version and resized sponsorship badges dynamically. |

### 6. Code Review Notes
Reviewing the Public Repo Showcase Corrections.
- **Sponsor Badges:** The Ko-Fi and BMC markdown syntax scaled up to 100% width on GitHub depending on screen sizes. Fixed by converting markdown injection into HTML tags setting `height="50"`.
- **Root README Synchronization:** Swapped out the technical setup documentation with the End-User facing document (`docs/product/README.md` and variants) to ensure the target audience doesn't receive complex Docker instructions.

---

## [PM] Next Steps — Prioritized Backlog

### 🟡 P1: Near-Term Feature Work
1. **GitHub Settings (BOSS):** Set description, website, and topics for the public repo `terranandes/marffet-app` if not already done.
2. **Accounts-Over-Time Chart** — Multi-portfolio net-worth tracking line chart (requested via Jira board / TBD).
3. **Phase C: AI Copilot Polish / Notification Triggers** — Advanced Copilot chat interfaces and email alerts configuration logic.

---

## [PL] Summary Report to Terran

> **Boss, here's the 2026-03-05 v1 sync update:**
>
> **Completed this session:**
> - ✅ Closed out **BUG-012** totally. Verified the `Home.*` strings correctly map to JSON values natively via Playwright on the live Zeabur URL.
> - ✅ Wiped out the E2E verification worktree (`test-full-test-local`) to keep our git directory clean.
> - ✅ Caught our mistake on the `marffet-app` Showcase. We purged the tech-heavy README from the public root and dynamically merged the End-User versions instead. Also wrangled the Ko-fi and Buy Me a Coffee button scales with explicit HTML height tags.
>
> **What's Next for Us:**
> The deployment and documentation are pristine. Next logical steps belong either to integrating the requested **Net-Worth Multi-Portfolio line chart** or digging into **AI Copilot Polish (Phase C)** to deliver true Tier differentiation value.
>
> What would you like us to attack next?

---

**Meeting adjourned at 00:41 HKT.**
