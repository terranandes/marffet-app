# Code Review: Clean Room & Cache Architecture
**Date**: 2026-02-03
**Reviewer**: [CV] Code Verification
**Topic**: MarketCache, Scraper V2, Engine Patch

---

## 1. `app/services/market_cache.py`
**Rating**: ⭐⭐⭐⭐⭐ (Excellent)
-   **Logic**: Uses a standard Singleton pattern (`_PRICES_CACHE` global).
-   **Efficiency**: Lazy loading prevents import-time lag. Reading from RAM is O(1).
-   **Safety**: Explicitly handles keys. The fallback logic for V1 vs V2 schema (`if "daily" in node`) is robust.
-   **Risk**: Thread safety on *write*? Currently Read-Only after startup. Safe.

## 2. `scripts/crawl_official.py` (V2 Upgrade)
**Rating**: ⭐⭐⭐⭐ (Good)
-   **Improvement**: Fetching `daily` data preserves the "Physics" of the market (Volatility).
-   **Minification**: Using keys `d, o, h, l, c, v` saves ~40% space vs `date, open...`. Good choice for JSON.
-   **Concern**: The `try/except` block inside `fetch_unadjusted_history` is a bit broad (`except Exception as e: continue`).
    -   *Recommendation*: In future, catch specific `yfinance` errors to differentiate "Network Error" vs "Delisted".

## 3. `app/main.py` (Engine Patch)
**Rating**: ⭐⭐⭐⭐ (Solid)
-   **Patch**: The check `if 'summary' in node: node = node['summary']` effectively creates a "View Adapter" for the old engine.
-   **Correctness**: Verified via `verify_full_stack.py`. TSMC CAGR Calculation remained consistent.
-   **Maintainability**: `run_mars_simulation` is getting large (~200 lines).
    -   *Recommendation*: Extract "Dividend Reinvestment Logic" into a separate helper class/method in Phase 5.

## 4. Overall Architecture
-   **Security**: No sensitive data (ISIN is public).
-   **Reliability**: Removing Excel dependency dramatically increases reliability.
-   **Test Coverage**: `verify_full_stack.py` covers the critical path (Data -> Cache -> Engine).

**Verdict**: **PASSED**. Ready for Production.
