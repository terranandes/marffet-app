# Code Review: 2026-02-01 (Post-Tidy-Up)

**Reviewer**: [CV] Agent  
**Scope**: `tests/` restructuring, `e2e_suite.py`, and `test_plan.md` updates.

---

## 1. Directory Structure (`tests/`)
**Rating: ⭐⭐⭐⭐⭐ (Excellent)**

The move from a flat `scripts/` + `tests/` mess to a structured hierarchy is a massive improvement.
-   `tests/unit`: Clearly separated.
-   `tests/integration`: Contains the verifiable logic (`test_fetch_names`).
-   `tests/debug_tools`: Good home for the one-off scripts (`debug_calc.py`).

**Observation**: `fix_imports.py` did a good job patching `sys.path`. However, we saw some fragility in `test_schema.py` (relative vs absolute imports) that required a second pass.
**Recommendation**: For future python files, enforce **Unit Tests runs from Root** (`uv run -m pytest`) to standardize import paths.

## 2. E2E Test Suite (`tests/e2e/e2e_suite.py`)
**Rating: ⭐⭐⭐ (Needs Improvement)**

-   **Issue 1 (Mobile Import)**: The script tried to import `test_mobile_portfolio` from `tests` or local, but it moved to `tests/unit`. We patched this, but it felt hacky.
-   **Issue 2 (Hardcoded Waits)**: `time.sleep(2)` is used frequently.
    -   *Risk*: Causes BUG-101 (Timeout) if API is slow (3s).
    -   *Fix*: Use `page.wait_for_response()` or `expect(locator).to_be_visible()`.
-   **Issue 3 (Selector Robustness)**:
    -   `page.get_by_text("+ New Group")`: If this text changes (e.g. translation), test breaks. Use `data-testid` where possible.

## 3. Unit Tests (`tests/unit/`)
**Rating: ⭐⭐ (Fragile)**

-   **Critical Flaw**: `test_cb_api.py` and others seem to make **real network calls**.
    ### Update (Session 2): Audit & Quarterly Sync

    **Reviewed Items:**
    1.  **Agent Rules Audit**:
        *   `GEMINI.md`: Fixed broken paths and removed strict mandate for `intelligent-routing` skill (verified fixed).
        *   `agent-assignment.md`: Added exception clause for role flexibility.
        *   *Verdict*: **PASSED**. Complies with project governance.

    2.  **Quarterly Sync Feature** (`app/services/backup.py`):
        *   **Logic**: `run_quarterly_dividend_sync` correctly chains `sync_all_caches` and `backup_dividend_cache`.
        *   **Scheduling**: APScheduler cron expression `0 0 1 1,4,7,10 *` is correct (Quarterly on 1st @ 00:00 system / 03:00 UTC implied).
        *   **Security**: Uses `GITHUB_TOKEN` safely.
        *   *Verdict*: **PASSED**.

    **Final Recommendation:**
    The release `c72d72b` is stable and ready for production use.
    -   *Evidence*: The test session hung for >60s.
    -   *Violation*: Unit tests must be fast and isolated.
    -   *Fix*: **Mandatory Mocking**. Use `unittest.mock` or `pytest-mock` to stub `yfinance` and `requests`.

## 4. Product Documentation
**Rating: ⭐⭐⭐⭐ (Good)**

-   `test_plan.md` is now aligned with reality.
-   `tasks.md` accurately tracks the "Fix Admin UX" completion.

---

## Summary
The codebase organization is healthy. The *Quality Assurance* layer (Tests) is the weak point right now. It is brittle and network-dependent.

**Priority**: Refactor `tests/unit` to be offline-capable (Mocking).
