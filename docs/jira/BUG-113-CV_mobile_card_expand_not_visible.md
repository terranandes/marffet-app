# BUG-113-CV: Mobile Card Expand Click — Element Not Visible

**Reporter**: [CV] Agent
**Date**: 2026-02-17
**Severity**: Low
**Status**: New

## Description

During automated Playwright Mobile E2E testing (iPhone 12 viewport), the "TSMC" card text is found in the DOM but reported as `not visible`, causing the expand-card click to timeout after 30 seconds.

## Steps to Reproduce

1. Open Portfolio at `/portfolio` in mobile viewport (390×844)
2. Create group "Mobile Test" → Add stock 2330 (TSMC)
3. Attempt to click `TSMC` text to expand card details → **TIMEOUT**

## Root Cause (Suspected)

The `TSMC` `<div>` resolved in DOM but was marked `not visible` by Playwright, suggesting either:
- CSS `overflow: hidden` or `display: none` applied to the parent container at mobile breakpoint
- The card content may be rendered off-screen or behind another element
- The Desktop table `<td>` containing "TSMC" is hidden but the mobile card's version may use a different selector

## Evidence

Playwright log:
```
locator resolved to <div class="font-bold text-white">TSMC</div>
58 × waiting for element to be visible - element is not visible
```

## Fix Suggestion

1. Investigate responsive CSS at the mobile breakpoint for StockCard component
2. Ensure `.first.click()` targets the mobile card's visible element, not the hidden desktop table row
3. Add `data-testid="mobile-stock-card"` for reliable mobile test targeting
