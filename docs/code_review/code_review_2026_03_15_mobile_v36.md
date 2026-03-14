# Code Review: Phase 36 Mobile UX Polish & Error Tracking
## Date: 2026-03-15 (v36)

> **Agent Tag:** [CV] / [PL]

### Summary of Changes Evaluated

This review corresponds to the mobile usability enhancements and stability patches introduced for the Marffet PWA. The primary goals were to resolve the static routing preference on load, fix unresponsive tab switches, establish loading transparency on data retrieval, and handle system crashes gracefully.

### 1. PWA Initial Route Preference (manifest.json)
*   **Change:** Updated `start_url` from `/mars` to `/`.
*   **Assessment:** [PASS] This was the root cause of the mobile home-screen shortcut forcing users to the Mars tab regardless of their `localStorage` default landing page setting. By defaulting to the root, Next.js can now orchestrate the redirect correctly.

### 2. Tab Switching Freezes (usePortfolioData.ts)
*   **Change:** Injected `{ keepPreviousData: true, fallbackData: ... }` into the `useSWR` configuration for `groups`, `targets`, and `dividendCash`.
*   **Assessment:** [PASS] Prior to this, rapid switching between tabs on mobile caused SWR to clear the cache momentarily while re-validating, leading to layout thrashing or perceived hanging. `keepPreviousData` ensures the UI remains populated (and interactive) while the background sync resolves.

### 3. Portfolio Loading States (page.tsx)
*   **Change:** Introduced explicit Skeleton UI blocks bound to the `loading` flag from the portfolio hook.
*   **Assessment:** [PASS] Eliminates the frustrating "blank screen" gap previously experienced when the network was slow retrieving target data.

### 4. Global Error Boundary Setup (error.tsx)
*   **Change:** Setup a React Global Error Boundary specifically for the App Router targeting root crashes (`app/error.tsx`).
*   **Assessment:** [PASS] The generic crash screen provides a native recovery button and a fallback dashboard link. Currently, errors are output to `console.error`. 
*   **Note for Security/Ops:** If comprehensive remote telemetry is required, we still need to decide on Sentry integration vs custom ingestion on the backend (Phase 37).

### Conclusion
The modifications closely adhere to the requirements of the `[UI]` and `[PM]` roles to establish a robust and polished mobile experience. The changes are minimal, targeted, and localized to the immediate UX blockers identified in the prior E2E run.

*Status: APPROVED for Push.*
