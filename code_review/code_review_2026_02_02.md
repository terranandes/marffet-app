# Code Review: 2026-02-02

**Reviewer:** [CV]
**Focus:** Cash Ladder & App Entry Points

## Critical Findings
### 1. Blocking I/O in Async Endpoint
*   **File:** `app/main.py` (Line 1043)
*   **Function:** `fetch_leaderboard`
*   **Issue:** The endpoint is defined as `async def`, which runs on the main event loop. However, it calls `get_leaderboard()`, which performs synchronous database operations (Blocking I/O).
*   **Impact:** During the database query, the entire application will pause, blocking other requests.
*   **Recommendation:** 
    *   **Option A (Quick):** Remove `async` keyword to use FastAPI's threadpool automatically.
    *   **Option B (Explicit):** Use `run_in_threadpool(get_leaderboard, limit)`.

## Improvements
### 1. Frontend Error Handling (User Experience)
*   **File:** `frontend/src/app/ladder/page.tsx`
*   **Observation:** Error logging relies on `console.error`. 
*   **Suggestion:** Add a visible toast notification for API failures (sync stats, fetch leaderboard) to improve user feedback.

## Verification
*   **Cash Ladder Logic:** Verified correct. Scripts `tests/integration/verify_ladder_backend.py` passed.
