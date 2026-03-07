# BUG-015: Infinite Rendering (Loading Skeletons) on Tab Switch
**Reporter:** [PL]
**Date:** 2026-03-07
**Component:** Frontend (Navigation / Page Rendering)
**Status:** Open

## Description
When navigating between tabs on either the mobile view or the desktop view, the application unnecessarily unmounts and remounts the page content, resulting in a constant "Rendering..." state (Skeleton loaders). The UI feels sluggish instead of instantaneously snapping between previously loaded views.

## Steps to Reproduce
1. Open the application.
2. Settle on any tab (e.g., Portfolio) and let it fully load.
3. Switch to another tab (e.g., Trend Dashboard).
4. Skeletons appear.
5. Switch *back* to Portfolio. Skeletons appear again instead of immediately showing cached data.

## Expected Behavior
Navigating between tabs should feel like a native mobile app. Previously visited tabs should retain their state or cache their data (e.g., via `SWR` or `React Query`) so that switching back is instantaneous without aggressive re-rendering. 

## Technical Context
- The `trend/page.tsx`, `myrace/page.tsx`, etc., all use raw `useEffect` and `fetch` calls paired with `useState` for loading state (`const [loading, setLoading] = useState(true)`).
- Every time the page route is hit via Bottom Tab Bar or Sidebar, Next.js mounts the Client Component fresh, triggering `setLoading(true)` and the network request over again.
- The lack of a global client-side data cache means every mount starts from scratch.

## Proposed Action Plan
1. Install `swr` (Stale-While-Revalidate) in the frontend.
2. Refactor the `fetch` logic in the main tabs (Portfolio, Trend, MyRace, BarChartRace, Compound, CB, CashLadder) to use `useSWR`.
3. This will immediately resolve the "infinite rendering" issue by instantly returning cached data for previously visited tabs while silently updating in the background.
