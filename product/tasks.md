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
- [x] **Tab: Compound Interest** (Implemented via Iframe Wrapper)
- [x] **Tab: MoneyCome Comparison** (Implemented via Modal in Mars Strategy)
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
    - [x] **CAGR Verification**: TSMC 18.8% (Realistic) vs previous halluncination. Correlation PROVEN.
- [ ] **Phase 4: Universal Data Lake (Daily Data)** <!-- id: 30 -->
    - [/] Upgrade Scraper to Store Daily OHLCV (Running...) <!-- id: 31 -->
    - [x] Update `MarketCache` to support Nested Schema (V2).
    - [x] Update App Logic to support Nested Schema (V2).
    - [ ] Update `Trend` and `Race` endpoints to use Daily Data.
## 5. Maintenance & workflows
- [x] **AI Copilot Fix** (Updated SDK discovery logic & injected Portfolio Context)
- [x] **Trend Page Data Fix** (Fixed NameError in `get_portfolio_history`)
- [x] **Bar Chart Race Local Fix** (Added missing numpy import)
- [x] **Full System Verification** (Verified all API endpoints locally)
- [x] **Admin "Rebuild & Push" Feedback Improvement**
- [ ] **Full Test Suite (Automated)** - `tests/e2e_suite.py` (Passing locally, verify on generic CI eventually)
- [x] **Sidebar Reordering** (Compound Interest moved)
