# BUG-007: Transaction Modal Timeout (Regression)

**Severity**: High
**Status**: Open
**Date**: 2026-01-25
**Reporter**: [CV]

## Description
During the `full-test` automated E2E run, the Transaction Modal failed to open (or was not interactive) on the Desktop view.
The test timed out waiting for the "Shares" input field after clicking "+Tx".

## Evidence
-   **Error**: `Locator.fill: Timeout 30000ms exceeded`
-   **Location**: `tests/e2e_suite.py` Test 3 (Add Transaction)

## Reproduction Steps
1.  Login as Guest.
2.  Create Group.
3.  Add Stock (e.g., 2330).
4.  Click "+Tx" button on the stock row.
5.  **Expected**: Modal opens, "Shares" field focusable.
6.  **Actual**: Timeout waiting for field.

## Notes
Possible cause: Z-index issue with the new Card View changes (even though this was desktop test) or recent Tailwind class updates.
