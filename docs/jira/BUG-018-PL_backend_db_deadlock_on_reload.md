# Bug Report: Backend Uvicorn/SQLite Deadlock on Reload

## 1. Description
During local testing and automated E2E verification, the FastAPI backend (`uvicorn`) frequently enters a zombie state upon reload or when the frontend proxy connection drops. This leaves the backend port (e.g., 8000 or 8001) hanging in `EADDRINUSE` and keeps the SQLite `portfolio.db` locked, causing subsequent requests to fail with 500 Internal Server Error.

## 2. Steps to Reproduce
1. Start the backend with `uvicorn app.main:app --reload`.
2. Connect a Next.js frontend proxy and generate significant traffic (e.g., via a Playwright automated script fetching `/auth/guest`).
3. Force-close or rapidly reload the frontend/Playwright script.
4. Try to access the backend API or run another query against the SQLite database.

## 3. Expected Behavior
The backend should cleanly release ports and file locks upon reload or when connections are dropped, allowing seamless development and testing.

## 4. Actual Behavior
The backend port remains open by an orphaned process, and the SQLite DB retains a `.db-wall` lock. The backend throws `[Errno 98] Address already in use` upon restart attempts, and a forceful `pkill -9` is required.

## 5. Potential Causes & Fixes
- `uvicorn` using `WatchFiles` reloader might not cleanly shutdown worker processes if a DB operation is pending.
- Connection pooling or SQLite connection sharing without proper teardown in the FastAPI `lifespan` context.

## 6. Priority / Severity
**Priority:** High
**Severity:** Critical (Blocks automated testing and requires manual intervention to restart environments)
