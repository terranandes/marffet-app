# Brainstorming: Universal MarketCache Migration

## Goal
Eliminate dependency on legacy file-based crawlers (`project_tw/crawler.py`) and unify all data access through `MarketCache` (sourced from `yfinance`).

## Key Decisions
1.  **Single Source of Truth**: `MarketCache` (L1) + `yfinance` Live (L2).
2.  **MoneyCome Logic**: Port `ROICalculator` to `app/services` and standardize inputs/outputs.
3.  **Admin Control**: Add "Backfill" button to Admin UI to trigger massive historical data download via `yfinance.download(batch)`.
4.  **Verification**: TSMC 22.2% CAGR is the golden master benchmark.

## Alternatives Considered
-   **Keep Legacy Crawlers**: Too brittle, scraping often breaks.
-   **New Scraper**: `yfinance` is more reliable and free.

## Action Plan
-   [x] Create Migration Plan.
-   [ ] Execute Phase 1 (Core Logic).
