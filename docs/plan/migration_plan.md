# Ralph Plan: Universal MarketCache & MoneyCome Migration

## Overview
Migrate the entire application to use `MarketCache` (yfinance source) as the single source of truth for historical data, and `MarketDataService` (Mix Strategy) for real-time data. Implement `MoneyCome` methodology via a standardized `ROICalculator` service. Eliminate legacy file-based crawlers from the critical path.

## Phase 1: Core Logic Migration
Refactor "Lab" code from `project_tw` into production `app/services`.

- [ ] **Create `app/services/roi_calculator.py`**
    - Move `ROICalculator` (from `project_tw/calculator.py`).
    - Standardize inputs (Pandas DataFrame) and outputs (Dict).
    - Ensure `calculate_complex_simulation` (Mars Logic) is preserved and tested.
- [ ] **Create `app/services/strategy_service.py`**
    - Implement `MarsStrategy` logic here.
    - **Crucial Change:** Replace `TWSECrawler`/`TPEXCrawler` dependency with `MarketCache` and `MarketDataService`.
    - Implement `analyze_stock_batch` using `MarketCache.get_prices_db()` for instant historical access.
    - Implement `get_comparison_data` for the Comparison Tab.

## Phase 2: Admin & Data Management
Empower Admin to manage data without legacy tools.

- [ ] **Implement Backfill Logic in `MarketDataService`**
    - Add `backfill_all_stocks(period: str = "max")` method.
    - Logic: Use `yfinance.download(tickers, group_by='ticker')` for massive batch fetch.
    - Split result by Year and update `data/raw/Market_{Year}_Prices.json`.
- [ ] **Update `app/routers/admin.py`**
    - Add `POST /admin/market-data/backfill` endpoint. (Triggers `crawl_backfill.py` logic but integrated).
    - Add `POST /admin/cache/refresh` (already exists, verify).

## Phase 3: Strategy API & UI Integration
Expose the new logic to the Frontend.

- [ ] **Create `app/routers/strategy.py`**
    - `POST /strategy/mars/analyze`: Trigger analysis (using `StrategyService`).
    - `GET /strategy/comparison`: Get comparison data for list of stocks.
- [ ] **Verify Live Tabs**
    - `Portfolio`: Ensure `MarketDataService.fetch_live_prices` is efficient (Batching).
    - `Race`: Verify `get_portfolio_race_data` uses `MarketCache`.
    - `Cash Ladder`: Verify current asset value source.

## Phase 4: Verification & Clean Up
Ensure 100% correctness.

- [ ] **Test: Universal Data Consistency**
    - Run `tests/e2e/test_universal_data.py`.
    - **Benchmark:** TSMC (2330) 2006-2025 CAGR must be **22.2%**.
- [ ] **Test: Real-Time Crawler**
    - Verify `MarketDataService` fetches *Today's* price if market is open.
- [ ] **Cleanup**
    - Deprecate/Remove `project_tw/crawler.py` usage in main app.
    - Archive `project_tw` or mark as Research only.
