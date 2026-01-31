
# Agent Sync Meeting - 2026-01-31

**Attendees:** [PL], [CODE], [PM], [SPEC], [UI], [CV]
**Focus:** Critical Incident (Zeabur Crash) & Project Status

## 1. Critical Incident Triage (Zeabur Crash)
**[PL]**: We have a confirmed outage on Zeabur immediately following the Batch Refactor. Errors: `ECONNRESET` / `socket hang up`.
**[CODE]**: I found the smoking gun in `app/routers/portfolio.py`.
- **The Bug:** `api_portfolio_race_data` is defined as `async def`.
- **The Trigger:** Inside it, we call `get_portfolio_race_data()`, which is **Synchronous** and now does a heavy **Batch Download** (blocking I/O).
- **The Result:** The Main Event Loop is blocked during the download. Any concurrent request (like `/auth/me` or Health Check) times out immediately. Zeabur's proxy kills the connection.
**[CV]**: Confirmed. In FastAPI, `async def` assumes non-blocking code. Blocking code must be wrapped or use `def` (which runs in threadpool automatically).
**[PL]**: Decision?
**[CODE]**: **Hotfix 3**. Wrap the call in `fastapi.concurrency.run_in_threadpool`.

## 2. Project Progress
- **Feature (My Race):** "Visual" logic works (Trend/Race). "Data" logic refactored to Batch.
- **Feature (Deployment):** Currently broken (Crash). Fix identified.
- **Feature (Negative Caching):** Deployed (Hotfix 1 & 2). effective against `65331` loops.

## 3. Discrepancy (Local vs Zeabur)
- **Local:** Single user, no strict health checks. Blocking loop was unnoticed.
- **Zeabur:** Strict proxy timeouts. Blocking loop kills the pod.

## 4. Action Items
1. **[CODE]**: Apply `run_in_threadpool` wrapper to `app/routers/portfolio.py`.
2. **[PL]**: Redeploy and Verify.
3. **[PM]**: Update User on status.

**Status:** RED (Fixing) -> GREEN (Expected after Hotfix 3).
