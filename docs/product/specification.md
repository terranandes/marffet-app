# Marffet Investment System - Technical Specifications
**Version**: 5.1
**Date**: 2026-03-13
**Owner**: [SPEC] Agent

## 1. System Architecture

Decoupled Client-Server architecture for containerized deployment (Zeabur).

### Feature Specifications Index

| Module | Spec Document | Status |
|:-------|:-------------|:-------|
| Mars Strategy & BCR | [Mars & BCR Feature Logic](./mars_strategy_bcr.md) | ✅ Production |
| Portfolio Tracker | [Portfolio Feature Spec](./feature_portfolio.md) | ✅ Production |
| Compound Simulator | [Compound Feature Spec](./feature_compound.md) | ✅ Production |
| Convertible Bonds | [CB Feature Spec](./feature_cb.md) | 🚧 Development |
| AI Copilot | [AI Copilot Feature Spec](./feature_ai_copilot.md) | ✅ Production |
| Leaderboard & Ladder | [Leaderboard Feature Spec](./feature_leaderboard.md) | ✅ Production |
| Admin Dashboard | [Admin Feature Spec](./feature_admin.md) | ✅ Production |
| Settings & User System | [Settings & User Spec](./feature_settings_user.md) | ✅ Production |
| Trend & My Race | [Trend & Race Feature Spec](./feature_trend_race.md) | ✅ Production |
| Auth Architecture | [Google OAuth & Guest Mode](./auth_db_architecture.md) | ✅ Production |
| DuckDB Data Lake | [DuckDB Architecture](./duckdb_architecture.md) | ✅ Production |
| Data Pipeline | [Crawler & Pipeline](./data_pipeline.md) | ✅ Production |
| Admin Operations | [Ops Manual](./admin_operations.md) | ✅ Production |

### 1.1 Components
| Component | Tech | Role | URL |
|-----------|------|------|-----|
| Backend | FastAPI (Python 3.12) | REST API, Auth, Simulation Engine | `marffet-api.zeabur.app` |
| Frontend | Next.js 16 (React 18) | UI, Visualization (ECharts), SSR | `marffet-app.zeabur.app` |

### 1.2 Authentication & App Lifecycle
- **Protocol**: OAuth 2.0 (Google)
- **Cookie**: `httpOnly`, `SameSite=None`, `Secure`
- **Option B (Strict Loading)**: An `<AuthGuard>` intercepts all private routes. If a user lacks a session (User or Guest), no background API calls, SWR fetches, or calculations are permitted. A global login prompt is shown instead.
- **Graceful Termination**: On logout, all in-flight API requests are forcibly aborted via `AbortController`, the global SWR cache is wiped, background polling is stopped, and the client router instantly redirects to home, guaranteeing zero side-effects.
- **Start Page Constraint**: The `MARS Strategy` tab is strictly prohibited from being set as the default start page to avoid resource-intensive loading on cold starts.

### 1.3 Access Control & Memberships

The system enforces a **5-tier access model** with strict precedence: `GM > VIP > PREMIUM > FREE > Guest`.

#### Tier Definitions

| Tier | Auth Required | How Assigned | Description |
|:-----|:-------------|:-------------|:------------|
| **Guest** | ❌ No login | Automatic | Unauthenticated visitor. Data stored in `localStorage` only. Severely limited. |
| **FREE** | ✅ Google OAuth | Automatic on sign-up | Standard registered user. Server-side data persistence. |
| **PREMIUM** | ✅ Google OAuth | `PREMIUM_EMAILS` env var or DB injection | Unlocks premium analysis and export features. |
| **VIP** | ✅ Google OAuth | `VIP_EMAILS` env var or DB injection | All PREMIUM features + priority support + future exclusive features (email alerts, early access). |
| **GM** | ✅ Google OAuth | `GM_EMAILS` env var only | Full admin powers: dashboard, membership injection, system operations, crawl controls. |

#### Feature Access Matrix

| Feature | Guest | FREE | PREMIUM | VIP | GM |
|:--------|:------|:-----|:--------|:----|:---|
| Mars Strategy | ✅ | ✅ | ✅ | ✅ | ✅ |
| Bar Chart Race | Basic | Basic | Advanced (CAGR) | Advanced (CAGR) | Full |
| Compound Interest (Single) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Compound Interest (Comparison) | 🔒 | 🔒 | ✅ | ✅ | ✅ |
| Portfolio Groups | 3 max | 11 max | 20 max | 30 max | ∞  |
| Targets per Group | 10 max | 50 max | 100 max | 200 max | ∞  |
| Transactions per Target | 10 max | 100 max | 500 max | 1,000 max | ∞  |
| AI Copilot | ❌ | Educator | Educator | Wealth Manager | Full |
| CB Notifications | ❌ | ❌ | ✅ In-App | ✅ In-App + Email | Full |
| Rebalancing Alerts | ❌ | ❌ | ✅ In-App | ✅ In-App + Email | Full |
| Data Export | ❌ | 📦 Unfiltered | 📥 Filtered + 📦 Unfiltered | 📥 Filtered + 📦 Unfiltered | Full |
| Server-Side Data | ❌ | ✅ | ✅ | ✅ | ✅ |
| Admin Dashboard | ❌ | ❌ | ❌ | ❌ | ✅ |
| Membership Injection | ❌ | ❌ | ❌ | ❌ | ✅ |

#### Precedence & Resolution
- **Precedence**: `GM > VIP > PREMIUM > FREE`. The highest available tier is always granted.
- **Static Assignment**: `GM_EMAILS`, `PREMIUM_EMAILS`, `VIP_EMAILS` environment variables provide immutable tier assignment.
- **Dynamic Assignment**: Manual injection via Admin Dashboard into the `user_memberships` table (`portfolio.db`). Supports durations: Monthly (30d), Annually (365d), Permanent (99y). Expired injections gracefully revert to the static tier.
- **Effective Tier**: `max(static_tier, injected_tier)`. The `/auth/me` endpoint computes and returns the effective `tier` string and `is_premium` boolean.
- **Sponsorship Integration**: Users sponsoring via Ko-fi or Buy Me a Coffee can have their VIP/PREMIUM status manually injected by the GM.

## 2. API Specification

### 2.1 Base URLs
| Environment | URL |
|-------------|-----|
| Production | `https://marffet-api.zeabur.app` |
| Local | `http://localhost:8000` |

### 2.2 Key Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/me` | GET | User session status |
| `/api/results` | GET | Mars Strategy simulation results |
| `/api/race-data` | GET | Flat race data for BCR (wealth, cagr, dividend) |
| `/api/stock/{id}/history` | GET | Raw price/dividend history |
| `/api/export/excel` | GET | Excel export with dynamic params |

### 2.3 Race-Data Response Format (v2.1)
```json
[
  {
    "id": "2383",
    "name": "台光電",
    "year": 2006,
    "wealth": 1000000,
    "value": 1000000,
    "dividend": 0,
    "cagr": 0,
    "roi": 0
  }
]
```
**Note**: Changed from nested `{year, stocks}` to flat format for legacy UI compatibility.

## 3. Simulation Engine

### 3.1 Key Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `start_year` | 2006 | Simulation start year |
| `principal` | 1,000,000 | Initial investment (TWD) |
| `contribution` | 60,000 | Annual contribution (TWD) |

### 3.2 History Output
- **Year Range**: `start_year` → 2026 (21 years inclusive)
- **Fields**: `year`, `value` (wealth), `dividend`
- Year 2006 added as initial investment point (v2.1 fix)

### 3.3 Corporate Actions
- **Split Detection**: Auto-detects splits via >40% overnight price drops.
- **Data Basis**: **100% Nominal (Unadjusted)**.
    - All prices in `daily_prices` must be the raw trading price at that date.
    - The engine handles dividend reinvestment and split adjustments *dynamically* during calculation.
    - Feeding adjusted prices (TRI) to the engine will lead to incorrect CAGR results.
- **Adjustment**: Adjusts share count cumulatively.

## 4. Notification Engine

The `NotificationEngine` evaluates user portfolios and generates alerts based on automated strategies. Alerts are fetched via `GET /api/notifications`.

### 4.1 Response Format (`upgrade_cta` example)
```json
{
  "id": "notice_cb_discount",
  "title": "CB Arbitrage Opportunity",
  "message": "Found 2 CBs with healthy premiums",
  "action_url": "/cb",
  "timestamp": "2026-03-24T12:00:00.000000Z",
  "is_read": false
}
```

### 4.2 Active Triggers (Global)
These triggers currently apply globally to all users:
- **SMA Pair Rebalancing (Gravity Alert)**: Identifies Overvalued (> +20% vs SMA 250) and Undervalued (< -20% vs SMA 250) assets. Suggests a 30% exchange pair trade.
- **Market Cap Rebalancing (Size Authority)**: Flags positions representing > 1.2x or < 0.8x the portfolio average market cap. Suggests a 30% exchange from High to Low cap.
- **Convertible Bond (CB) Arbitrage**:
  - *Arbitrage*: CB Premium < -1% (Suggests Buy CB, Sell Stock).
  - *Strong Sell*: CB Premium >= 30% (Suggests Sell CB, Buy Stock).

### 4.3 Legacy Triggers (`RuthlessManager`)
- An orphaned engine (`RuthlessManager` in `engines.py`) exists with legacy Premium-only restrictions but is currently inactive and not scheduled.

## 5. Deployment Strategy

### 4.1 Services
| Service | Build | Env Vars |
|---------|-------|----------|
| Backend | `Dockerfile` (root) | `GOOGLE_CLIENT_ID`, `SECRET_KEY`, `FRONTEND_URL` |
| Frontend | `frontend/Dockerfile` | `NEXT_PUBLIC_API_URL` |

### 4.2 Environment Variables
| Variable | Service | Example |
|----------|---------|---------|
| `FRONTEND_URL` | Backend | `https://marffet-app.zeabur.app` |
| `NEXT_PUBLIC_API_URL` | Frontend | `https://marffet-api.zeabur.app` |
| `SECRET_KEY` | Backend | `long_random_string` |

## 5. Changelog

### v5.1 (2026-03-13) - Dividend Sync Fix & Guest Mode Round 4
- **Dividend Sync Fix**: Resolved mapping discrepancy where the backend nested `total_cash` but the frontend expected `total_dividend_cash` in the target summary.
- **Guest Mode Architecture**: Finalized refactor to strictly use `localStorage`. Backend `users` table no longer stores "guest@local" entries.
- **Mobile E2E**: Verified Round 4 Guest Flow on mobile viewport with refined Playwright locators.

### v5.0 (2026-03-03) - Marffet Rebrand & Tier Matrix Formalization
- **Rebrand**: Renamed Martian → Marffet across frontend, backend, i18n, localStorage keys, and all product documentation.
- **Tier Matrix**: Formalized the complete 5-tier access model (Guest → FREE → PREMIUM → VIP → GM) with detailed feature access matrix.
- **Compound Interest Gating**: Comparison Mode gated behind PREMIUM+ tier.
- **URL Update**: All references updated to `marffet-app.zeabur.app` / `marffet-api.zeabur.app`.

### v4.2 (2026-03-02) - Admin Membership & Sponsorship
- **Membership Injection**: Added manual VIP/PREMIUM injection via Admin Dashboard (`user_memberships` in `portfolio.db`).
- **Tier Precedence**: Implemented strict `GM > VIP > PREMIUM` logic merging static `.env` settings with dynamic database records.
- **Sponsorship Links**: Added Buy Me a Coffee and Ko-fi links in the UI `SettingsModal` and `Sidebar` to facilitate user upgrades.

### v4.1 (2026-03-01) - Phase E: Purple Sweep + Skeleton Loading
- **Color Palette Enforcement**: Removed all 21 purple/violet CSS references across 10 files. Replaced with warm palette (amber, cyan, teal, emerald, rose).
- **Skeleton Loading States**: Added shared `Skeleton.tsx` component (5 variants). Applied animated skeleton placeholders to 6 pages (mars, race, trend, ladder, myrace, viz).
- **Premium Emails**: Server-side `PREMIUM_EMAILS` environment variable for granting premium access by email.
- **BUG-004-UI**: Transaction date picker dark mode confirmed fixed (`colorScheme: dark`).

### v3.0 (2026-02-07) - Phase 3 Verification Complete
- **Split Detector Implementation**: Auto-detects >40% overnight drops, verified 0050 CAGR >12%.
- **MarketCache Singleton**: Zero-latency price lookups across all tabs (O(1) performance).
- **First Close Buy Logic**: Verified compliance with MoneyCome comparison mode.
- **Comprehensive E2E Testing**: 15 integration tests + Playwright suite (Desktop/Mobile) - 100% pass rate.
- **numpy JSON Serialization Fix**: Resolved 500 errors in `/api/results` endpoint.

### v2.3 (2026-01-31)
- **Dynamic Stock Naming**: Real-time alignment with TWSE/TPEX data (No more hardcoded maps).
- **Convertible Bond (CB) Support**: Full support for CB tickers (e.g., 11011).
- **Admin Sync Ops**: Enhanced "Smart Update" to always refresh stock list.
- **Directory Consolidation**: Unified python logic in `app/project_tw`.


### v3.1 (2026-02-07) - Compound Interest Refinement
- **Compound Page Native Implementation**: Replaced iframe with full native Next.js + ECharts implementation.
- **MoneyCome Correlation**: Validated engine logic against MoneyCome.in rules.
- **Total Investment Fix**: Corrected formula to `Principal + ((EndYear - StartYear + 1) * Contribution)` (Inclusive counting).
- **Dividend Logic**: Verified cash dividends based on held shares and reinvestment at yearly average price.

## 6. Compound Interest Logic

### 6.1 Core Formulas
- **Total Investment**: `Principal + ((End_Year - Start_Year + 1) × Annual_Contribution)`
  - *Note:* Contribution is applied on the *Start Year* as well (Inclusive).
- **ROI**: `(Final_Value - Total_Investment) / Total_Investment × 100%`
- **CAGR**: `(Final_Value / Initial_Principal)^(1 / Years) - 1`

### 6.2 Dividend Reinvestment Rules (MoneyCome Standard)
- **Cash Dividends**: Calculated based on *held shares from the previous year* (留倉部位).
- **Reinvestment Price**: Cash dividends are reinvested at the *average price of the current year* (當年均價).
- **Stock Dividends**: Added directly to share count (Par $10 base).

### 6.3 Buying Strategies
- **BAO (Buy At Opening)**: Buy at yearly opening price (Jan 1st). Used for Comparison Mode.
- **BAH (Buy At Highest)**: Buy at yearly highest price (Worst case).
- **BAL (Buy At Lowest)**: Buy at yearly lowest price (Best case).
