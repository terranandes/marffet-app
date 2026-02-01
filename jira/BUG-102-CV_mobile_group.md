# Bug Report: Mobile Test Group Selection

**ID**: BUG-102-CV_mobile_group
**Reporter**: [CV]
**Date**: 2026-02-01
**Component**: Tests / Mobile
**Severity**: High

## Description
`tests/unit/test_mobile_portfolio.py` fails to find the Group Tab "Mobile Test" after creation.
Error: `❌ Group 'Mobile Test' tab not found!`

## Steps to Reproduce
1. Run `uv run tests/unit/test_mobile_portfolio.py`
2. Observe output.

## Root Cause Logic
The test creates a group but maybe the sidebar logic or tab visibility on mobile viewport (width 390) hides it or requires a drawer toggle.

## Evidence
- Console output: `❌ Group 'Mobile Test' tab not found!`

## Resolution
Fixed in `frontend/src/app/portfolio/page.tsx` by enabling horizontal scrolling (`overflow-x-auto`) for group tabs on mobile instead of wrapping.
Verified with `tests/unit/test_mobile_portfolio.py`.

## Status
Resolved (2026-02-01)
