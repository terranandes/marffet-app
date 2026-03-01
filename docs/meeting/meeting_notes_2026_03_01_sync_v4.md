# Agents Sync Meeting - v4
**Date:** 2026-03-01 15:57 HKT
**Topic:** Portfolio Data Refresh Fix, Code Review, BOSS_TBD New Directives

## Attendees
- **[PM] Terran**: Product strategy, new BOSS_TBD directives
- **[PL] (Antigravity)**: Meeting orchestration, branch cleanup
- **[SPEC]**: Architecture review
- **[CODE]**: Backend fix (transaction_repo.py)
- **[UI]**: Frontend hooks & cache-busting refactor
- **[CV]**: Code review, Jira audit, TypeScript verification

---

## 1. Project Live Progress (`docs/product/tasks.md`)
- **Phase F (Portfolio Beautification)**: ✅ Complete.
- **BUG-011-CV (Transaction Edit)**: ✅ Fixed. Backend `list_transactions` query was missing `target_id` in SELECT, causing the edit form modal to never open.
- **Portfolio Data Refresh**: ✅ Fixed. Two root causes addressed:
  1. Next.js `fetch()` was caching GET responses by default; added `cache: "no-store"` + `_cb=${Date.now()}` cache-busters to all portfolio API reads.
  2. `groupStats` was stored as separate React state, not updating when individual targets refreshed; refactored to `useMemo` derived from `targets` array.
- **AICopilot Build Fix**: ✅ Bonus fix. `ReactMarkdown` no longer accepts `className` prop in latest version; moved class to wrapper `div`.

## 2. Bug Triage & Jira Status

| ID | Description | Status |
|----|-------------|--------|
| BUG-000 | Local Frontend Env | ⚠️ No explicit status |
| BUG-001 | Remote Copilot Auth | ⚠️ No explicit status |
| BUG-002 | BCR Duplicate Year Data | ✅ CLOSED |
| BUG-003 | Portfolio Dividend Sync NaN | ✅ CLOSED |
| BUG-004 | Transaction Date Picker Style | 🟡 OPEN |
| BUG-005 | Trend Portfolio Value Mismatch | ✅ CLOSED |
| BUG-006 | My Race Target Merge Name Bug | ✅ CLOSED |
| BUG-007 | Cash Ladder UI/UX Bugs | ✅ CLOSED |
| BUG-008 | AnimatePresence Missing Import | ✅ CLOSED |
| BUG-009 | Playwright Execution Crash | ⚠️ No explicit status |
| BUG-010 | Mobile Portfolio Card Click Timeout | 🟡 OPEN (Deferred) |
| BUG-011 | Portfolio Transaction Edit Failure | ✅ CLOSED |

**Summary:** 7/12 CLOSED, 2/12 OPEN, 3/12 status unclear (likely resolved but not formally closed).

## 3. Code Review Summary (Today's 2 Commits)
- **11 files changed**, 66 insertions, 42 deletions.
- **`transaction_repo.py`**: Added `target_id` to SELECT — minimal, correct, no side effects.
- **`usePortfolioData.ts`**: `useMemo` refactor is idiomatic React. Removes duplicated stats calculation from `fetchTargets`. Clean.
- **`portfolioService.ts`**: Added `cache: "no-store"` and `_cb` to 7 fetch calls. Consistent pattern (mirrors existing `getDividends` which already had it). No regression risk.
- **`AICopilot.tsx`**: Moved `className` from `<ReactMarkdown>` to parent `<div>`. TypeScript-clean (`bunx tsc --noEmit` passes).
- **Verdict:** ✅ PASS — All changes are focused, minimal, and correctly scoped.

## 4. Branch & Worktree Cleanup
- ✅ Deleted stale branch `full-test-local` (was e6d224b).
- ✅ Deleted stale branch `local-test` (was 5d75d0e).
- No active worktrees remain. No stashes. Master is clean.

## 5. New BOSS_TBD Directives (from Terran)
Boss added 6 new items to the Barrier section of `BOSS_TBD.md`:
1. **Rename to Marffet?** — Decision pending from Boss.
2. **GitHub Publish** — Exchange `docs/product/README*.md` ↔ `./README.md` for public-facing repo. No code/tech stack leakage.
3. **Buy-Me-Coffee Button (Web App)** — Link to `buymeacoffee.com/terwu01`.
4. **Buy-Me-Coffee Button (GitHub README)** + MIT License consideration.
5. **AICopilot Enhancement** — Not detailed yet.
6. **Test Google Cloud Run** — Alternative to Zeabur.
7. **DB/Warm Static files/Locally cached files optimization**.
8. **Email support**.

## 6. Features Unimplemented / Deferred
- [ ] Compound Interest tab (BOSS_TBD)
- [ ] Cash Ladder tab review (BOSS_TBD)
- [ ] Multi-language (Deferred)
- [ ] RuthlessManager integration (Premium-only notification logic, currently orphaned)
- [ ] Free vs Paid notification tier separation

## 7. Deployment Status
- Master is up-to-date with `origin/master` at commit `2a86587`.
- Zeabur should auto-deploy. No known discrepancies between local and deployed.

---

## Next Actions (Post-Meeting)
1. [PL] Run `document-flow` if specs/docs need updating.
2. [PL] Execute `commit-but-push` workflow.
3. [PM] Await Boss decision on Marffet rename, Buy-Me-Coffee, and GitHub publish.
4. [CODE] Formally close BUG-000, BUG-001, BUG-009 or triage for re-investigation.
5. [UI] Address BUG-004 (date picker style) when convenient.
