# Martian Investment System - Technical Specifications
**Version**: 4.0
**Date**: 2026-02-17
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
| Backend | FastAPI (Python 3.12) | REST API, Auth, Simulation Engine | `martian-api.zeabur.app` |
| Frontend | Next.js 14+ | UI, Visualization (ECharts), SSR | `martian-app.zeabur.app` |

### 1.2 Authentication
- **Protocol**: OAuth 2.0 (Google)
- **Cookie**: `httpOnly`, `SameSite=None`, `Secure`
- **CORS**: Backend allows specific Frontend origin

### 1.3 Access Control & Memberships
- **Tiers**: `FREE`, `PREMIUM`, `VIP`, `GM` (Game Master)
- **Precedence Logic**: `GM` > `VIP` > `PREMIUM`. The highest available tier is always granted.
- **Assignment Mechanisms**:
  1. **Static (Environment Variables)**: `GM_EMAILS`, `PREMIUM_EMAILS`, `VIP_EMAILS` configure immutable access.
  2. **Dynamic (Database Injection)**: Manual injection via Admin Dashboard into the `user_memberships` table (`portfolio.db`). Supports varying durations (monthly, annually, lifetime) and automatic expiration handling.
- **Sponsorship Integration**: Users sponsoring via Ko-fi or Buy Me a Coffee can have their VIP/PREMIUM status manually injected by the GM.

## 2. API Specification

### 2.1 Base URLs
| Environment | URL |
|-------------|-----|
| Production | `https://martian-api.zeabur.app` |
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

### 4.1 Active Triggers (Global)
These triggers currently apply globally to all users:
- **SMA Pair Rebalancing (Gravity Alert)**: Identifies Overvalued (> +20% vs SMA 250) and Undervalued (< -20% vs SMA 250) assets. Suggests a 30% exchange pair trade.
- **Market Cap Rebalancing (Size Authority)**: Flags positions representing > 1.2x or < 0.8x the portfolio average market cap. Suggests a 30% exchange from High to Low cap.
- **Convertible Bond (CB) Arbitrage**:
  - *Arbitrage*: CB Premium < -1% (Suggests Buy CB, Sell Stock).
  - *Strong Sell*: CB Premium >= 30% (Suggests Sell CB, Buy Stock).

### 4.2 Legacy Triggers (`RuthlessManager`)
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
| `FRONTEND_URL` | Backend | `https://martian-app.zeabur.app` |
| `NEXT_PUBLIC_API_URL` | Frontend | `https://martian-api.zeabur.app` |
| `SECRET_KEY` | Backend | `long_random_string` |

## 5. Changelog

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
