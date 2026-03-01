# Code Review Note - v4
**Date:** 2026-03-01
**Reviewer:** [CV] / [PL]

## Verdict
**PASS** — Portfolio Data Refresh & Transaction Edit Fixes

## Commits Reviewed
1. `26775af` — fix(portfolio): include target_id in transaction history fetch to fix edit button
2. `2a86587` — fix(portfolio): refresh data via cache disabled and derived stats hook; fix(ai): react markdown class prop

## Files Reviewed (11 files, 66+/42-)

### Backend
- **`app/repositories/transaction_repo.py`** (+1/-1): Added `target_id` to the `list_transactions` SELECT query. Minimal change; no regression risk. The column is indexed as part of the WHERE clause anyway. ✅

### Frontend — Data Layer
- **`frontend/src/services/portfolioService.ts`** (+11/-7): Applied `cache: "no-store"` and `_cb=${Date.now()}` cache-buster to 7 GET fetch calls inside `ApiPortfolioService`. Pattern is consistent with the already-existing `getDividends` call (line 263). No changes to `GuestPortfolioService` (uses localStorage, not fetch). ✅
- **`frontend/src/app/portfolio/hooks/usePortfolioData.ts`** (+22/-24): Refactored `groupStats` from `useState` to `useMemo` derived from `targets`. Removed duplicate calculation from `fetchTargets`. Correct React pattern — `useMemo` dependency is `[targets]`, ensuring recalculation on any `setTargets` update. ✅

### Frontend — UI
- **`frontend/src/components/AICopilot.tsx`** (+1/-2): Moved `prose prose-sm prose-invert` classes from `<ReactMarkdown className=...>` (invalid in react-markdown v9+) to the parent `<div>` wrapper. TypeScript compilation passes. ✅

## Security & Performance
- Cache-busting via `_cb` param is a standard pattern. No server-side implications (FastAPI ignores unknown query params).
- The `useMemo` refactor slightly reduces re-renders by avoiding explicit `setGroupStats` after `setTargets`.
- No authentication or authorization changes detected.

## Observations
- BUG-000-CV, BUG-001-CV, BUG-009-CV lack explicit `**Status:**` lines in their Jira files. Recommend formal status reconciliation.
- BUG-004-UI (date picker style) is still OPEN. Low severity, cosmetic only.
