# Bug Report: Unit Test Hang (CB API)

**ID**: BUG-103-CV_unit_hang
**Reporter**: [CV]
**Date**: 2026-02-01
**Component**: Tests / Unit
**Severity**: Medium

## Description
`pytest tests/unit/` hangs indefinitely (or > 60s) on `tests/unit/test_cb_api.py`.

## Investigation
- Likely due to unmocked external network calls to TWSE/TPEX within the CB API test.
- `TestClient` might be hitting live routes that attempt to fetch/cache data synchronously or with long timeouts.

## Resolution
Fixed in `tests/unit/test_cb_api.py` by using `FastAPI.TestClient` and mocking `CBStrategy` + `DB`.
Tests now run in <1s with no network dependency.

## Status
Resolved (2026-02-01)
