# Code Review: Ralph Loop Migration

**Date:** 2026-02-11
**Reviewer:** AntiGravity [CV]
**Scope:** MarketCache Migration (Ralph Loop)

## Summary
The "Ralph Loop" successfully migrated the core pricing logic to `MarketCache` (yfinance) and ported the `MoneyCome` ROI logic. The system passes the "Golden Master" E2E test for TSMC.

## 1. Core Logic (`app/services/roi_calculator.py`)
- **Status:** ✅ Functional & Verified
- **Observations:**
    - Ported `calculate_complex_simulation` successfully.
    - **Technical Debt:** Split detection logic is complex and flagged as "suspicious" in comments, though it matches legacy behavior.
    - **Improvement:** `_get_detector` global singleton pattern is brittle. consider dependency injection.

## 2. Strategy Service (`app/services/strategy_service.py`)
- **Status:** ✅ Functional
- **Observations:**
    - Uses `MarketCache` for prices (Good).
    - **Violation:** Still uses `TWSECrawler` for dividends. PRD goal "Eliminate legacy crawlers" is only partially met.
    - **Critical Debt:** Hardcoded dividend patches (lines 95-110) for TSMC/0050/etc. exist in the code. These should be moved to a configuration file or the database (`dividend_overrides` table).

## 3. API & Main (`app/main.py`)
- **Status:** ✅ Functional
- **Observations:**
    - Legacy `run_mars_simulation` (line 854) remains in `main.py`. This creates code duplication with `StrategyService`.
    - New routers (`strategy`, `admin`) are correctly wired.

## 4. Verification
- **E2E Test:** `tests/e2e/test_universal_data.py` PASSED (TSMC CAGR ~22.2%).
- **Unit Tests:** `tests/unit/test_roi_calculator.py` PASSED.

## Actionable Recommendations
1.  **Refactor Dividends:** Move hardcoded dividend patches to `data/dividend_patches.json` or DB.
2.  **Unify Logic:** Replace `run_mars_simulation` in `main.py` with calls to `StrategyService` to ensure a single source of truth.
3.  **Split Logic:** Add comprehensive unit tests specifically for Stock Splits to validate the "suspicious" logic.
