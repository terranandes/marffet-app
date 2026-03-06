# BUG-014-CV: Mobile Top Bar/Bottom Bar Visibility in Playwright

**Reporter:** [CV] Agent
**Date:** 2026-03-06
**Status:** OPEN

## Description
The `tests/e2e/test_phase31_ui.py` verification script for Phase 31 Mobile App-Like Experience fails to find the mobile Top Bar or Bottom Bar elements during Playwright automated testing.

## Steps to Reproduce
1. Start the application locally.
2. Run a script using a mobile viewport (e.g., iPhone 12, 390x844).
3. Attempt to locate `get_by_text("Marffet")` or BottomTabBar text elements (`"Mars"`, `"More"`).

## Expected Behavior
The Mobile Top Bar and Bottom Tab Bar are correctly rendered and visible in the Playwright DOM.

## Actual Behavior
Playwright resolves the elements as hidden (`14 × locator resolved to hidden`). It's possible the elements are occluded, using incorrect responsivity breakpoints for the Playwright viewport size, or text is structurally nested in ways `get_by_text` fails to verify as visible.

## Environment
- Local worktree (`CV_full-test-local`)
- Playwright Chromium Mobile Viewport (iPhone 12)
