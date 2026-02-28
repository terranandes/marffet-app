# BUG-999
**Reporter:** [CV]
**Type:** Test Flakiness / Execution Crash
**Description:** Playwright Execution Crash on `http://localhost:3001`: Timeout 30000ms exceeded.
**Details:** During the headless E2E bug hunt via `tests/e2e/mcp_bug_hunt.py` on the isolated git worktree, the `page.wait_for_load_state('networkidle')` step timed out across the Next.js frontend dev server (likely due to persistent hot-reload websocket connections keeping the network active).
**Recommendation:** Migrate `networkidle` waits to `domcontentloaded` or explicit element visibility checks when running against the `next dev` development server.
