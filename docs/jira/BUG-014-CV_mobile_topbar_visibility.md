# BUG-014-CV: Mobile Top Bar/Bottom Bar Visibility in Playwright

**Reporter:** [CV] Agent
**Date:** 2026-03-06
**Status:** FIXED

## Description
Mobile Top/Bottom Bar elements were reported as hidden in Playwright. Verified as FIXED on 2026-03-13 via successful Phase 31 UI automated tests. All elements found and visible in mobile viewport.

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
