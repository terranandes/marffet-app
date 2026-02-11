# Bug Report: UI Modal Stuck

**ID:** BUG-012-CV_ui_modal_stuck
**Reporter:** [CV]
**Date:** 2026-02-11
**Severity:** Medium
**Evidence:** `tests/evidence/error_modal_stuck.png`

## Description
During E2E testing of the "Full Test Local" workflow, the Playwright suite captured a screenshot `error_modal_stuck.png`. This indicates that a modal (likely "Mars Strategy" or "Transaction" modal) failed to close or became unresponsive, causing the test flow to hang.

## Steps to Reproduce
1.  Run `e2e_suite.py`.
2.  Navigate to Portfolio/Strategy.
3.  Trigger Modal action.

## Impact
- Blocks automated E2E verification.
- User might experience stuck UI if backend latency is high or frontend state is desynchronized.

## Proposed Fix
- Investigate frontend console logs for JS errors.
- Add timeout/close logic to modals in frontend code.
- Ensure backend responses are robust (handle timeouts).
