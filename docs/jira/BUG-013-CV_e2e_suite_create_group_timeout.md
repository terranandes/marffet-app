# BUG-013-CV: E2E Suite Create Group Timeout

**Reporter:** [CV] Agent
**Date:** 2026-03-06
**Status:** OPEN

## Description
The `tests/e2e/e2e_suite.py` test fails during `TEST 1: Create Group` with a timeout when waiting for the created group name to become visible.

## Steps to Reproduce
1. Start the application locally.
2. Run `uv run python tests/e2e/e2e_suite.py`.

## Expected Behavior
The script successfully clicks "+ New Group", enters a name, clicks "Create", and the new group "E2E Test Group" appears in the UI.

## Actual Behavior
The script times out waiting for `get_by_text("E2E Test Group")` to be visible after clicking create. The test also logs `Guest Mode Badge NOT found`, which implies the Guest context might not be active, preventing local storage group creation.

## Environment
- Local worktree (`CV_full-test-local`)
- Playwright Chromium Headless
