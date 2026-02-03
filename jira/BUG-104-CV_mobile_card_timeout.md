# BUG-104-CV_mobile_card_timeout

**Reporter**: [CV]
**Date**: 2026-02-02
**Status**: Open
**Priority**: Medium

## Description
During the automated E2E run (`e2e_suite.py`), the "Mobile Verification" step logged a timeout error when looking for the 'TSMC' card.

```
❌ Mobile Card NOT found (Timeout)
```

However, the test continued to "Card Expanded" and eventually "Mobile Test Complete". This suggests race condition or extreme UI latency on the Mobile View (Portfolio Card).

## Steps to Reproduce
1. Run `python3 tests/e2e/e2e_suite.py`
2. Wait for Mobile Browser launch.
3. Observe finding 'TSMC' card.

## Impact
Users might perceive the UI as "Empty" for 5-10 seconds before cards render on mobile.
