# PRD: Ralph Loop - Refactoring & Unification

**Phase:** 2 (Refactoring)
**Date:** 2026-02-11
**Objective:** Unify strategy execution logic, eliminate legacy code duplication, and harden critical components.

## 1. Problem Statement
The initial migration successfully ported core logic to `StrategyService`, but `app/main.py` still relies on a duplicated, legacy function `run_mars_simulation`. This violation of "Single Source of Truth" risks inconsistent results between the API (`/mars/analyze`) and the Legacy UI endpoints (`/api/results`, `/api/race_data`). Additionally, dividend logic relies on hardcoded patches and legacy crawlers.

## 2. Goals
1.  **Eliminate Code Duplication:** Remove `run_mars_simulation` from `app/main.py`.
2.  **Unify Execution:** Update all `app/main.py` endpoints to use `app/services/strategy_service.py`.
3.  **Harden Logic:** robustness tests for Split Detection and Dividend Patching.

## 3. Scope & Tasks

### Task 2.1: Enhance Strategy Service
- **Refactor:** Ensure `MarsStrategy.analyze()` supports the output formats required by Legacy UI (or provide transformation helpers).
- **Dividend Service:** Abstract dividend fetching/patching. Ensure `data/dividend_patches.json` is loaded reliably.
- **Performance:** Ensure `MarsStrategy` caching matches the performance needs of `main.py`.

### Task 2.2: Refactor `app/main.py` (The Big Switch)
- **Replace:**
    - `get_results` -> calls `MarsStrategy().analyze`
    - `get_race_data` -> calls `MarsStrategy().analyze`
    - `api_export_excel` -> calls `MarsStrategy().analyze`
- **Delete:** `run_mars_simulation` function definition.
- **Verify:** Ensure JSON structure of API responses remains **identical** to avoid breaking Frontend.

### Task 2.3: Verification Improvements
- **New Test:** `tests/unit/test_split_detector.py` covering:
    - Normal splits (e.g., 2:1)
    - Reverse splits (if any)
    - Cumulative ratio calculation
- **Regression Test:** `tests/integration/test_main_refactor.py` comparing Old vs New output (if possible, or just verifying New output against known values).

## 4. Verification Plan
- **Manual:** Run the App, check "Trend" and "My Race" tabs.
- **Automated:**
    - `tests/e2e/test_universal_data.py` must still pass (Golden Master).
    - New `tests/unit/test_split_detector.py` must pass.

## 5. Success Metrics
- `app/main.py` has ZERO lines of simulation logic (only routing).
- All endpoints return 200 OK.
- TSMC 2006-2025 CAGR remains ~22.2%.
