# BUG-023-CV_mobile_portfolio_selector_ambiguity.md

**Reported by:** [CV] Code Verification Manager
**Date:** 2026-03-19
**Severity:** P3 — Warning (non-blocking, all 12 passes PASSED)
**Area:** [Area E] Portfolio CRUD — Mobile Viewport

---

## Summary

The `wait_for_selector` in `verify_area_e()` of `round7_full_suite.py` uses an overly broad selector that ambiguously resolves to sidebar navigation links on mobile viewports instead of actual portfolio content. This causes a spurious 15-second timeout warning on every mobile pass (Guest, terranfund, terranstock).

---

## Root Cause

```python
# Line 124 — BEFORE (ambiguous):
await page.wait_for_selector(
    ".glass-card, button[role='tab'], [class*='portfolio'], [class*='group']",
    timeout=15000
)
```

The `[class*='group']` part matches sidebar `<a>` elements that use Tailwind's `group` utility class (e.g., `class="flex items-center gap-3 px-4 py-3 rounded-xl ... group ..."`). On mobile, these nav links are rendered as the first 15 visible elements, causing the selector to "succeed" but point to the wrong element. The subsequent `asyncio.sleep(3)` then completes against a non-portfolio element, resulting in the 15-second timeout log before finally timing out after 35 resolution cycles.

---

## Fix Applied

```python
# AFTER (specific to portfolio page content):
await page.wait_for_selector(
    "main .glass-card, [data-testid='portfolio-main'], h1, .portfolio-header, .animate-pulse",
    timeout=15000
)
```

This targets elements that only appear in the portfolio page `<main>` container, not in sidebar navigation.

---

## Status

- **Fixed** in `round7_full_suite.py` line 124.
- **Committed** and pushed to `master`.
