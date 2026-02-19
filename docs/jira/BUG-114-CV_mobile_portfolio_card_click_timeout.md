# BUG-114-CV: Mobile Portfolio Card Click Timeout

**Reporter**: [CV]
**Date**: 2026-02-19
**Severity**: 🟡 Medium
**Status**: Open
**Phase**: Phase 8 (Mobile Premium Overhaul)

---

## Summary

Mobile portfolio test fails with a `Locator.click: Timeout 30000ms exceeded` error when attempting to click the TSMC stock card.

## Steps to Reproduce

1. Run `uv run python3 tests/e2e/e2e_suite.py`
2. Observe the mobile portfolio test (`tests/unit/test_mobile_portfolio.py`)
3. After adding TSMC to portfolio, the test tries to click the TSMC card

## Error

```
💥 Error: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_text("TSMC", exact=True).first
    - locator resolved to <div class="font-bold text-white">TSMC</div>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is not visible
    - retrying click action
```

## Root Cause Analysis

The TSMC card element is **found** (locator resolves) but is **not visible** — likely hidden behind another element or off-screen in the mobile viewport. This is consistent with BUG-113 (mobile card expand not visible).

## Related Bugs

- BUG-113-CV: Mobile card expand not visible (same symptom, different element)
- BUG-104-CV: Mobile card timeout (earlier version of same issue)

## Suggested Fix

- Check if the stock card is scrolled out of view in mobile viewport
- Use `scroll_into_view_if_needed()` before clicking
- Or use `force=True` in the click if the element is covered by another element

## Notes

- All other E2E tests passed (Guest Mode, Create Group, Add Stock, Add Transaction, Trend, Mars, BCR tabs)
- This is a test infrastructure issue, not necessarily a production bug
- Deferred to Phase 8 (Mobile Premium Overhaul)
