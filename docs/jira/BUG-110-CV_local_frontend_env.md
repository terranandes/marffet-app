# BUG-110-CV_local_frontend_env

**Reporter:** [CV] Code Verification Manager
**Component:** Frontend Configuration (Local Isolated Worktree)
**Priority:** Low (Affects local E2E testing only; Zeabur Production is stable)

## Description
When executing the full E2E parity test suite (`verify_task2_parity.py`), the local Next.js frontend (`localhost:3000`) spun indefinitely on "Calculating..." and "Loading race data..." for the Mars Strategy and Bar Chart components. 

The background `localhost:8000/api/results` endpoint was manually verified via `curl` to return HTTP 200 with data, confirming DuckDB hydration. The issue stems from the Next.js `dev` environment failing to route its internal API calls to the local Uvicorn instance, likely due to a missing or misconfigured `.env.local` inside the frontend directory.

## Evidence
- `tests/evidence/task2_mars_local.png`
- `tests/evidence/task2_bar_local.png`

## Expected Behavior
The local UI should render the data populated from the copied `market.duckdb` file exactly as the remote Zeabur application correctly did in `tests/evidence/task2_mars_remote.png`.

## Recommended Action
Ensure `.worktrees/full-test/frontend/.env.local` is explicitly generated during the worktree setup script in the `/full-test` workflow to define `NEXT_PUBLIC_API_URL=http://localhost:8000`.
