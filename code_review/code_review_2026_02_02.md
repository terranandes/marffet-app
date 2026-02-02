# Code Review - 2026-02-02
**Reviewer**: [CV] (Code Verification Manager)
**Topic**: Bun Migration & Tab Refactoring

## 1. Bun Migration
### Artifacts Reviewed
*   `frontend/Dockerfile`
*   `start_app.sh`
*   `frontend/package.json`
*   `mcp_config.json`

### Findings
*   **[CRITICAL] Redundant Lock File**: `frontend/package-lock.json` exists alongside `bun.lock`.
    *   **Risk**: Potential for dependency drift if `npm` is inadvertently used.
    *   **Recommendation**: `git rm frontend/package-lock.json`.
*   **[PASS] Dockerfile**: Correctly switched to `oven/bun:1`. `bun install --frozen-lockfile` is best practice.
*   **[PASS] Start Script**: `start_app.sh` properly checks for `bun` binary and uses `bun run --bun dev`.

## 2. Refactoring (StockDetailModal)
*   **[PASS] Logic**: Tab state management (`activeTab`, `compoundSubTab`) is clean.
*   **[PASS] URLs**: MoneyCome URLs are correctly formatted.
*   **[NOTE] Iframe**: Ensure `allow-scripts` and `same-origin` policies are safe (current implementation is standard).

## 3. Backup Logic
*   **[PASS] Scheduler**: Misfire grace time reduced to `3600` (1h). This is a correct fix for the "duplicate backup after restart" issue.

## 4. Testing
*   **[WARN] Hardcoded Paths**: `e2e_suite.py` had a hardcoded absolute path.
    *   **Fix**: [PL] already corrected this to `os.path.join`.
*   **[WARN] Timeouts**: 30s timeout on remote E2E indicates performance bottlenecks or cold start issues.

## Verdict
**Migration Status**: **APPROVED** (Subject to `package-lock.json` removal).
