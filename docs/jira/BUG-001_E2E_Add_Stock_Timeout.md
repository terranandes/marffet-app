# Bug Report: E2E Test Failure - Add Stock Timeout

**ID:** BUG-001
**Date:** 2026-01-20
**Environment:** Production (Zeabur) / Headless Chromium

## Description
The automated Playwright verification suite failed at the "Add Stock" step.
The script successfully opened the "Add Stock" modal (implied by progress) but failed to click the "Add" confirmation button.

## Error Log
```
💥 Error: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("div[role='dialog'] button").filter(has_text="Add")
```

## Evidence
- `1_landing.png`: ✅ Landing Page Loaded
- `2_logged_in.png`: ✅ Guest Login Successful (Sign Out button visible)
- `3_portfolio_view.png`: ✅ Portfolio Table Loaded

## Analysis
- **User Impact:** Low (User confirmed manual addition is possible).
- **Root Cause:** Playwright selector `div[role='dialog'] button text="Add"` likely does not match the actual UI.
- **Recommendation:** Inspect the "Add Stock" modal DOM. The button might be named "Confirm", "Submit", or have a different structure.

## Status
- **Fix:** Pending selector update in `tests/e2e_suite.py`.
