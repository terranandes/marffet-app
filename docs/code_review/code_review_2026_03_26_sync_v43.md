# Code Review - 2026-03-26 v43

## [CV] Review of Phase 41 SWR & Rendering Fixes

### 1. `frontend/src/app/portfolio/components/TargetList.tsx` & `TargetCardList.tsx`
- **Issue**: Extraneous usage of Framer Motion `staggerChildren` layout variants for dynamic array lists. When SWR `mutate()` pushes new row data, motion boundaries failed to update initial layout constraints, causing all incoming rows to render invisible.
- **Resolution**: Removed `motion.tr` wrappers on the individual target iterations. Using standard `<tr>` tags immediately resolves the visibility issue while decreasing component hydration latency.
- **Approval**: APPROVED.

### 2. `frontend/src/services/portfolioService.ts`
- **Issue**: `GuestPortfolioService` tries to enrich LocalStorage targets with `fetch("/api/portfolio/prices")` but lacks an internal timeout. If network changes interrupt `127.0.0.1:8000`, the `fetch` holds the SWR `Promise.all` indefinitely, freezing the `isValidating` badge in the UI.
- **Resolution**: Implemented native `AbortController` and `setTimeout(abort, 3000)`. If prices take longer than 3s to return from DuckDB bindings, it gracefully aborts and defaults `livePrice = null`, freeing the SWR hook to return cleanly to the UI.
- **Approval**: APPROVED. Robust and essential for remote testing scenarios.

### Summary
The code changes strictly target memory/promise leaks and layout discrepancies. The solution passes fundamental UI safety constraints. Proceed to commit.
