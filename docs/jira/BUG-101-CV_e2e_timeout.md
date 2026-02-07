# Bug Report: E2E Suite Timeout

**ID**: BUG-101-CV_e2e_timeout
**Reporter**: [CV]
**Date**: 2026-02-01
**Component**: Tests / E2E
**Severity**: Medium

## Description
`tests/e2e/e2e_suite.py` fails with `Timeout 30000ms exceeded`.
Screenshot logs suggest failure during "Add Transaction" verification or "verify holdings".

## Steps to Reproduce
1. Run `uv run tests/e2e/e2e_suite.py`
2. Observer failure after ~30s.

## Expected Behavior
Test completes within 30s or handles wait periods gracefully.

## Evidence
- Console output: `💥 Error: Timeout 30000ms exceeded.`

## Resolution
Fixed in `tests/e2e/e2e_suite.py`:
1. Replaced flaky `networkidle` with `domcontentloaded` + specific element waits.
2. Removed `expect_response` calls which failed in Guest Mode (no network traffic).
3. Refined assertions to filter for `visible=true` to handle Mobile/Desktop DOM duplication.
4. Corrected expected text for shares ("1000" instead of "1,000").

## Status
Resolved (2026-02-01)
