# PRD: Universal MarketCache & MoneyCome Migration

## Overview
Migrate the entire application to use `MarketCache` (yfinance source) as the single source of truth for historical data, and `MarketDataService` (Mix Strategy) for real-time data. Implement `MoneyCome` methodology via a standardized `ROICalculator` service. Eliminate legacy file-based crawlers from the critical path.

**Scope Coverage:**
- **Tabs:** Mars (start_year param), Comparison, Portfolio (Live), Race (My Race), Cash Ladder, Trend, Admin.
- **Strategies:** MoneyCome (Mars), CB Strategy (Yield Hunter), Compound Interest (Sim).
- **Visualization:** Bar Chart Race (BCR).
- **Ops:** Backfill, Cache Refresh, User Settings, Export Excel (Filtered).
- **AI:** Mars AI Copilot (Context Verification).



## Task 1: Core Logic Implementation (ROICalculator)
Standardize the calculation logic.
- [ ] Create `app/services/roi_calculator.py`.
- [ ] Port `ROICalculator` class from `project_tw/calculator.py`.
- [ ] Ensure `calculate_complex_simulation` (Mars Logic) is preserved and tested.
- [ ] Write Unit Test: `tests/unit/test_roi_calculator.py` verifying known CAGR inputs/outputs.

## Task 2: Strategy Service (Mars & CB Logic)
Implement the Mars Strategy using the new Calculator and MarketCache.
- [ ] Create `app/services/strategy_service.py`.
- [ ] Implement `MarsStrategy` class.
    - **Param:** `analyze(stock_ids, start_year=2006)`.
    - **Export:** `export_to_excel(filtered_data)` -> Returns Excel binary.
- [ ] Implement `CBStrategy` (Convertible Bond) logic.
- [ ] Inject `MarketDataService` (for `MarketCache` access).
- [ ] Implement `analyze(stock_ids)` method that:
    - Fetches history from `MarketCache`.
    - Fetches dividends (legacy patch + DB).
    - Runs `ROICalculator`.
    - Applies `filter_and_rank` logic from old `mars.py`.


## Task 3: Admin & Backfill
Empower Admin to refresh data.
- [ ] Update `app/routers/admin.py`.
- [ ] Implement `POST /admin/market-data/backfill`.
- [ ] Implement `MarketDataService.backfill_all_stocks(period='max')`.
    - Use `yfinance.download` batching.
    - Save to `data/raw/Market_{Year}_Prices.json`.

## Task 4: API & Integration
Expose data to the Frontend.
- [ ] Create `app/routers/strategy.py`.
    - `POST /strategy/mars/analyze`: Accepts `start_year`.
    - `POST /strategy/export`: Exports filtered Excel.
- [ ] **Verify Live Tabs Data Source**:
    - **Portfolio**: `get_portfolio_snapshot` (Live Prices).
    - **Trend**: `get_portfolio_history` (Monthly snapshots).
    - **My Race**: `get_portfolio_race_data` (Historical + Live).
    - **Cash Ladder**: `get_portfolio_ladder` (Asset distribution).
    - **Bar Chart Race (BCR)**: Ensure `get_race_data` uses `MarketCache` + `ROICalculator`.


## Task 5: Verification
Ensure Golden Master compliance.
- [ ] Update `tests/e2e/test_universal_data.py`.
- [ ] Assert TSMC (2330) CAGR is 22.2% (±0.1%) for 2006-2025.
## Task 6: User Settings & Persistence
Support cross-device settings via Backend.
- [ ] **Update DB Schema:** Add `settings` (JSON) or `api_key` column to `users` table.
- [ ] **Update `app/repositories/user_repo.py`**: Add `update_user_settings`.
- [ ] **Create `app/routers/user.py`**:
    - `POST /api/user/settings`: Save preferences (Theme, API Key).
    - `GET /api/user/settings`: Retrieve.

## Task 7: AIBOT Connection (Mars AI)
Ensure AI Copilot has access to the Unified Data.
- [ ] **Verify `POST /api/chat` Context**:
    - Ensure Frontend injects `MarketCache` derived data (Portfolio Snapshot) into the context.
- [ ] **Enhance `PROMPT_PREMIUM`**:
    - (Optional) detailed Review of the prompt to ensure it aligns with MoneyCome logic.

