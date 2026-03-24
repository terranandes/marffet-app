# Bug Report: Mobile E2E Test Failure on Tab Selection

**Issue ID:** BUG-020
**Reporter:** `[CV]`
**Component:** QA / Testing Infrastructure
**Severity:** Low (Affects QA scripts, not production logic)

## Description
During the `full-test` execution inside the `.worktrees/full-test-local` branch, the Desktop E2E suite (`tests/e2e/e2e_suite.py`) passed successfully. However, the chained `test_mobile_portfolio.py` failed with a `TimeoutError`.

## Root Cause
The mobile test attempts to assert if a `Mobile Test` group exists. If it exists in the DOM but is hidden (e.g., pushed off-screen in the mobile horizontal scroll layout), the script fails to click it and logs `Group 'Mobile Test' tab not found!`.
Consequently, the script attempts to interact with the Ticker input (`page.get_by_placeholder("Ticker (e.g. 2330)")`), but fails via timeout because the UI state prevents the button/input from becoming visible. 

Playwright error:
```
💥 Error: Locator.wait_for: Timeout 5000ms exceeded.
Call log:
  - waiting for get_by_placeholder("Ticker (e.g. 2330)") to be visible
```

## Recommended Fix
Update `test_mobile_portfolio.py` to:
1. Ensure the mobile viewport correctly implements `el.scroll_into_view_if_needed()`.
2. Or rewrite the locator logic to select the first visible group instead of requiring an exact string matching `Mobile Test`.

## Status
✅ **CLOSED (2026-03-19)** — Fixed in `tests/unit/test_mobile_portfolio.py` by switching to first-visible group selection with `scroll_into_view_if_needed()`. All mobile E2E passes verified in Phase 37 Round 7.
