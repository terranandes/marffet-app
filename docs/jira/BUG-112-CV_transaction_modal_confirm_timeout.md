# BUG-112-CV: Transaction Modal "Confirm" Button Timeout

**Reporter**: [CV] Agent
**Date**: 2026-02-17
**Severity**: Medium
**Status**: New

## Description

During automated Playwright E2E testing on Desktop (1280×800), the Portfolio Transaction modal's "Confirm" button could not be located by `get_by_text("Confirm")`, causing a 30-second timeout.

## Steps to Reproduce

1. Navigate to `/portfolio` (Guest Mode)
2. Create group → Add stock 2330 (TSMC)
3. Click `+Tx` button → Modal opens
4. Fill `shares=1000`, `price=500`
5. Click "Confirm" → **TIMEOUT** (button text not matching)

## Root Cause (Suspected)

The button text may have changed (e.g., "Save", "Add Transaction", or localized text) or the button may be outside the viewport in the modal. The Playwright locator `get_by_text("Confirm")` does not match the actual button label.

## Evidence

Screenshot: `tests/evidence/error_snapshot.png`

## Fix Suggestion

1. Inspect the actual button text in the Transaction Modal component
2. Update `e2e_suite.py:TEST 3` locator to match the real button label
3. Consider adding `data-testid="confirm-transaction"` for test stability
