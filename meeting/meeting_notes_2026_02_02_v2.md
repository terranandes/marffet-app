# Agents Sync Meeting Notes - 2026-02-02

**Topic**: Bun Migration & Deployment Sync
**Attendees**: [PM], [PL], [SPEC], [CODE], [UI], [CV]

## 1. Project Progress
*   **[PL]**: Successfully migrated frontend build system from Node.js to **Bun**.
*   **[PL]**: Renamed "MoneyCome" tab to "Compound Interest" and implemented sub-tabs (Single/Comparison).
*   **[PL]**: Fixed backup scheduler logic (reduced misfire grace time) to prevent duplicate backups.

## 2. Bun Migration Review
*   **[CV] Audit**:
    *   `mcp_config.json`: ✅ Updated to use `bunx` for ephemeral tools.
    *   `frontend/Dockerfile`: ✅ Updated base image to `oven/bun:1`.
    *   `start_app.sh`: ✅ Updated checking and running commands to use `bun`.
    *   `README.md`: ✅ Updated prerequisites.
    *   `product/software_stack.md`: ✅ Updated technology stack.
    *   **Flagged**: `frontend/package-lock.json` still exists. **Action**: Delete it to avoid confusion with `bun.lock`.

## 3. Bugs & Triages
*   **[CV] E2E Tests**:
    *   **Local**: Validated partial success after fixing `e2e_suite.py` path issue. Mobile test timed out (likely perf/env issue).
    *   **Remote (Zeabur)**: `TimeoutError` when looking for "New Group" button.
    *   **Diagnosis**: Remote DB might be clean/empty. Automation expects specific state or UI latency is higher than 30s timeout.
    *   **Action**: [CODE] to investigate `setup_test_data.py` or similar for reliable E2E seeding.

## 4. Deployment Status
*   **[PL]**: Pushed to `master` (Zeabur).
*   **[CV]**: Verification pending successful deployment and E2E pass.
*   **Discrepancy**: Local runs fine with Bun. Remote needs confirmation of successful Docker build with Bun.

## 5. Mobile Web Review
*   **[UI]**: New "Compound Interest" tab layout needs verification on mobile width.
*   **[UI]**: "Comparison" iframe scrolling behavior on iOS needs checking.

## 6. Action Items
1.  **[CODE]**: Remove `frontend/package-lock.json`.
2.  **[CV]**: Re-run E2E on Zeabur once stable.
3.  **[PL]**: Monitor backup logs tomorrow morning (Taipei Time) to confirm fix.

---
**Reported by**: [PL]
