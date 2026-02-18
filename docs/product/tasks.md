# Martian Project Tasks
**Owner:** [PL] Project Leader
**Status:** Active

## 1. Immediate Stabilization (Auth & DB Recovery) - [COMPLETED]
- [x] **Fix Login Loop (Cookie Domain)** (`Domain=None` for localhost/Zeabur compatibility)
- [x] **Fix DB Crash (Missing Columns)** (Implemented Self-Healing Schema in `portfolio_db.py`)
- [x] **Fix Logout Redirect** (Implemented Smart Redirect & enforced HTTPS)
- [x] **Fix Frontend Fetch Logic** (Switched to Relative Paths for Cross-Domain support)
- [x] **Verify Localhost Login/Logout** (Legacy: 8000, App: 3000)
- [x] **Verify Zeabur Remote Login/Logout** (Legacy: `martian-api`, App: `martian-app`)

## 2. Next.js Migration Verification - [COMPLETED]
- [x] **Guest Mode localStorage Sync**
- [x] **Settings Modal Alignment** (Feedback Tab, Default Page, Leaderboard)
- [x] **Mobile Responsiveness Check** (Sidebar Relative Paths)

## 3. Pending User Verification (BOSS)
- [x] **Mobile Login/Logout Correctness** (Zeabur)
    - *Note:* Infrastructure is ready. Pending final user check on actual device.

## 4. Feature Roadmap (Next Steps)
- [x] **Tab: Compound Interest** (Native Implementation with ECharts & MoneyCome Rules)
- [x] **Tab: MoneyCome Comparison** (Implemented via Native Calculation Engine)
- [x] [UI] Mobile or narrow screen portfolio card view
- [x] [UI] Align setting modal from legacy to Next.js UI
- [x] [UI] Trend alignment with Legacy UI (Curve Chart)
- [x] [UI] Ensure Tab CB is functionally working (Backend API Fixed)
- [x] [UI] Cash Ladder check (Leaderboard Architecture Verified)
- [x] [UI] My Race check (Market Value & Full Timeline implemented)
    - *Fix:* Added robust suffix resolution (e.g. `00937B` -> `.TWO`) for ETFs.
    - *Fix:* **Refactored to "Trend Architecture"** (In-Memory Calc) to eliminate "Socket Hang Up" and OOM crashes on Zeabur.
- [x] **Scraper Implementation (Phase 2)** (Official TWSE/TPEx Source) <!-- id: 1 -->
    - [x] Basic Logic (yfinance unadjusted)
    - [x] Dynamic Stock Naming (ISIN Source Implementation) - *Clean Room Flow*
    - [-] Legacy Data Fetching (Handling Delisted Stocks - Deferred per Brainstorming)
- [x] **App Optimization**: Implemented `MarketCache` (In-Memory) to solve JSON I/O latency.
    - *Note:* Shared singleton ensures data is reused across all concurrent users and all feature tabs (Trend/Race/Correlation).
- [x] [UI] Totally migration to Next.js UI. Remove legacy UI.
- [x] **Dynamic Stock Naming** (Integrated into Phase 2 Scraper) <!-- id: 2 -->
- [x] **Mars Strategy: Correlation (Phase 3)** (App Integration & Caching) <!-- id: 24 -->
    - [x] Integrated `MarketCache` for 0-latency daily price lookups.
    - [x] Verified `ROICalculator` uses Unadjusted Prices (TSMC ~60).
    - [x] **Split Detection Implemented**: Auto-detects >40% drops. 0050 CAGR fixed (12.1%).
    - [x] **CAGR Verification**: TSMC 19.0% (Realistic) vs previous halluncination. Correlation PROVEN.

## 5. Phase 6: Universal Data Lake (Daily Data) - [COMPLETED]
- [x] **Universe Backfill** (yfinance Prices + Dividends, 2000-Present)
    - [x] Smart Merge logic (`_merge_data_dict`, `overwrite=False` default)
    - [x] Dividend extraction via `yfinance` `actions=True`
    - [x] Stock Split → Stock Dividend rate conversion
- [x] **Admin Dashboard Enhancement**
    - [x] Safe Mode toggle (default ON)
    - [x] `POST /api/admin/market-data/backfill` API endpoint
    - [x] Progress polling via shared `CrawlerService` state
- [x] **Ultra-Fast Crawler** (`crawl_fast.py`) - Asyncio + Batch Implementation
- [x] Update `MarketCache` to support Nested Schema (V2).
- [x] Update App Logic to support Nested Schema (V2).
- [x] Update `Trend` and `Race` endpoints to use Daily Data (via `MarketCache` + `market_data_service`).
- [x] **Clean Code Optimization**: Removed direct `yfinance` dependencies from Backend Layers.
- [x] **Global Data Verification** ("Verify Everywhere"): Refactor `main.py` to remove direct Excel reads and enforce `MarketCache`.

## 6. Phase 7: DuckDB Core Migration - [COMPLETED]
- [x] **Replace JSON Engine with DuckDB Columnar DB**
    - [x] Solve Zeabur OOM (2.7GB → 100MB usage target)
    - [x] V9 Arrow/Pandas Turbo migration script (Ingested 6.5M rows)
    - [x] Unified `MarketDataProvider` (Single source of truth)
- [x] **Market Data Accuracy Recovery**
    - [x] Verified TSMC 2010 Daily Data (No longer monthly approximation)
    - [x] Unified `Dividends` table with Yearly/Quarterly sync support
- [x] **Cleanup & Operational Rigor**
    - [x] Deleted 2.7GB of fragmented JSON files
    - [x] Dropped `race_cache` from SQLite
    - [x] Revamped `supplement_prices.py` to target DuckDB directly

## 14. Phase 14: Nominal Price Standardization - [COMPLETED]
- [x] **MI_INDEX Mass Fetch (Nominal Source)**
    - [x] Implement `fetch_mi_index_mass.py` with WAF protection
    - [x] Execute fetch for 2004-2025 (Daily Checkpoints)
- [x] **Database Rebuild (Nominal Basis)**
    - [x] Purge `daily_prices` adjusted data
    - [x] Rehydrate from MI_INDEX snapshots → **5,025,797 rows, 1,629 stocks, 326 MB**
- [x] **Post-Rebuild Steps**
    - [x] Gap-Fill: 16 gaps filled, 0 failures (5,398 trading days)
    - [x] Dividend Import: 14,007 records from TWSE official API
- [ ] **Verification & Sync**
    - [x] `correlate_mars.py` fixed and running (TSMC 19.4% ≈ 18.8% ref)
    - [x] Grand Correlation v4 (>90% target — needs MoneyCome ref recalibration)
    - [ ] Direct DB Upload to Zeabur (Bypass Cloud Fetch)

## 7. Phase 8: Premium UI & Remote Stabilization - [PAUSED]
- [ ] **Zeabur Volume Persistence**
    - [ ] Configure volume mount for `/data` to persist `market.duckdb`
    - [ ] Final Remote Verification of TSMC CAGR (~19%)
- [ ] **Interactive Backfill Dashboard**
- [ ] **Mobile Premium Overhaul**

## 8. Maintenance & Workflows
- [x] **AI Copilot Fix** (Updated SDK discovery logic & injected Portfolio Context)
- [x] **Trend Page Data Fix** (Fixed NameError in `get_portfolio_history`)
- [x] **Bar Chart Race Local Fix** (Added missing numpy import)
- [x] **Full System Verification** (Verified all API endpoints locally)
- [x] **Full Test Suite (Automated)** - `tests/e2e/e2e_suite.py` + `tests/integration/test_all_tabs.py` (Passed 100% locally)
- [x] **Sidebar Reordering** (Compound Interest moved)
- [x] **Fix 6415 Detail API Crash** (Resolved Backend 500 error due to Numpy JSON serialization)
- [x] **Project Structure Cleanup** (Moved scripts to `tests/`, consolidated logs in `tests/log/`)
- [x] **Fix BUG-111: Next.js API Proxy 500 Error** (Resolved: Port mismatch fixed .env -> 8000) <!-- id: bug-111 -->

## 15. Phase 15: DuckDB Optimization & Dividend Migration - [COMPLETED]
- [x] **Dividend Migration (Single Source of Truth)**
    - [x] Retire `dividends_all.json` & hardcoded `DIVIDENDS_DB`
    - [x] Implement `MarketDataProvider.load_dividends_dict()` (DuckDB read)
    - [x] Update `app/main.py` (Remove legacy loader)
    - [x] Update `MarsStrategy` to skip live crawling (DuckDB read)
    - [x] Update all test/debug scripts
- [x] **Data Population**
    - [ ] Run `reimport_twse_dividends.py` (Pending Phase 14 Rebuild)
- [x] **Tab Audit**
    - [x] Confirm all tabs use DuckDB for prices
    - [x] Migrate Portfolio Dividend Sync from yfinance to DuckDB (Future Optimization)

## 16. Phase 16: Data Integrity Finalization (2000-2025) - [COMPLETED]
- [x] **Fix 2005-01-03 Data Cliff** (Major Anomaly)
    - [x] Investigate V12 (2004) vs Phase 14 (2005+) price discontinuity
    - [x] Resolve 60-99% drops for 1316, 2348, 3701, etc. (Purged 242 stocks)
- [x] **Fix "Bad Ticks"** (1,565 High-Frequency Glitches)
    - [x] Delete V-shape price spikes (>15% drop + immediate >85% recovery)
    - [x] Example: 0050 on 2024-01-25 (134 -> 81 -> 135) - Fixed
- [x] **Fix Missing Splits** (679 Persistent Drops)
    - [x] Patch L-shape price drops (>15% drop + stable low)
    - [x] Example: 0050 on 2025-06-18 (188 -> 47, 4-for-1 split) - Patched
- [x] **Full Validation**
    - [x] Run `benchmark_mars_simulation.py` (24-year full history) - 12.25s
    - [x] Verify CAGR >85% match with MoneyCome reference (TSMC 18.6%)

## 17. Phase 17: Grand Correlation, Zeabur Deployment & Nightly Pipeline - [NEXT]
> Ref: [Implementation Plan](file:///home/terwu01/.gemini/antigravity/brain/cdb129a3-7dbe-4f7d-a2a9-90d43225661c/implementation_plan.md)

### Part A: Grand Correlation vs MoneyCome Reference
- [x] **Create `correlate_all_stocks.py`** (NEW)
    - [x] Load UNFILTERED Excel (`stock_list_s2006e2026_unfiltered.xlsx`) — 2,385 stocks
    - [x] Compare `s2006e2026bao` (MoneyCome CAGR) vs our BAO CAGR
    - [x] Report: match rate 62.9% (±1.5%), 78.8% (±3.0%), MAE=2.17%
    - [x] Output `correlation_report_full.csv` saved to `docs/product/`
- [x] **Fix split double-counting** in `calculator.py`
    - [x] SplitDetector falsely detected stock dividends as splits → added guard
- [x] **Fix dividend timing** (去年留倉部位 rule)
    - [x] Dividends calculated on last year's position, before new investment
- [x] **Fix CAGR year alignment** — use `s2006e2026bao` to match reference
- [ ] **Fix TWT49U `權息` parser** (crawler.py L850-855 zeroes combined dividends)
    - [ ] 50+ stocks missing ≥5 years of dividends due to this bug
    - [ ] Re-run reimport after parser fix → expected match rate improvement
- [ ] **Re-run Grand Correlation v5** after dividend data fix

### Part B: Local Web App Verification (BOSS)
- [ ] Start backend: `uvicorn app.main:app --port 8000`
- [ ] Start frontend: `cd frontend && bun run dev`
- [ ] BOSS verifies: Mars tab, BCR tab, Export Excel, Compound Interest tab

### Part C: Zeabur Deployment (Persistent DuckDB)
- [ ] **Zeabur Volume Mount**: Configure persistent volume at `/data/`
- [ ] **Rehydration Logic in `app/main.py`** (MODIFY)
    - [ ] On startup: check if `/data/market.duckdb` exists
    - [ ] If missing → REHYDRATE from `data/backup/*.parquet` (bundled in image)
    - [ ] If exists → use existing (preserves daily updates)
- [ ] **Parquet Backup for Git** (Part D prerequisite)
    - [ ] Create `backup_duckdb.py` — Export DuckDB → yearly `data/backup/prices_YYYY.parquet` (<50MB each)
    - [ ] Check in `data/backup/*.parquet` to Git (DO NOT check in `market.duckdb`)
- [ ] **Push to `origin/master`** (after Parquet backup)
- [ ] **Verify Zeabur Remote**: TSMC CAGR ~19%, Mars tab, Auth flow

### Part D: Nightly Pipeline & Backup
- [ ] **Create `backup_duckdb.py`** (NEW)
    - [ ] `COPY (SELECT * FROM daily_prices WHERE year=YYYY) TO 'data/backup/prices_YYYY.parquet'`
    - [ ] Each yearly file <50MB, Git-friendly
- [ ] **Modify `refresh_current_year.sh`** (cron)
    - [ ] Add step: `supplement_splits.py --apply` after crawl
    - [ ] Add step: `backup_duckdb.py` before git push
- [ ] **Add Admin Backup Trigger** (`POST /api/admin/backup/trigger`)
- [ ] **Pipeline Flow**: Crawl → Split Supplement → Parquet Backup → Git Push

### Part E: Housekeeping - [COMPLETED]
- [x] **Commit Phase 16 scripts to `master`**
- [x] **Clean up 6 stale branches** (Local branches deleted; remote kept due to SSH issue)
- [x] **Kill lingering zombie Python processes**
- [x] **Remove redundant `SAVE_INTERVAL`** at L755 in `market_data_service.py`
- [x] **Gate debug prints** (Commented out high-volume prints)
- [x] **Fix bare `except` clauses** (L909, L919) in `market_data_service.py`

