# BUG-008: Mobile Login Overlay Viewport Obstruction

**Severity**: Medium
**Status**: Open
**Date**: 2026-01-25
**Reporter**: [CV]

## Description
Mobile verification tests on iPhone 12 viewport fail to interact with the "Continue as Guest" button.
Validations fail with `Element is outside of the viewport`, even when `force=True` is applied.

## Evidence
-   **Error**: `Locator.click: Element is outside of the viewport`
-   **Context**: Mobile Safari/Chrome emulation (390x844).

## Impact
Prevents automated mobile testing. Actual user impact might be lower (touch vs click event handling), but indicates a potential layout overflow or z-index layering invalidity on small screens.

## Proposed Fix
Review the `z-index` of the Login Overlay vs the `loading-msg` or other global containers in `layout.tsx` or `page.tsx`.
