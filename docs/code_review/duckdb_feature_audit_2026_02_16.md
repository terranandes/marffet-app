# DuckDB Feature Audit — 2026-02-16
**Auditor:** [CV] (Code Verification Agent)
**Scope:** All tabs, functions, and features — Data Source Mapping

---

## Audit Summary

| Category | Count | Status |
|----------|-------|--------|
| DuckDB (Corrected Data) | 11 features | ✅ Confirmed |
| yfinance (Real-Time / Sync) | 3 features | ⚠️ Expected, future optimization |
| External API (TWSE / Gemini) | 3 features | ✅ Expected |
| SQLite (User Data) | 5 features | ✅ Expected |
| Legacy Dead Code | 1 class | 🧹 Can be removed |

---

## Detailed Feature Audit

### ✅ DuckDB-Powered Features (Corrected Nominal Data)

| Feature / Tab | API Endpoint | Data Source | Function Chain |
|--------------|-------------|-------------|---------------|
| **Mars Strategy** | `GET /api/results` | DuckDB | `MarsStrategy.analyze()` → `MarketDataProvider.get_daily_history()` |
| **Simulation Detail** (Compound Interest) | `GET /api/results/detail` | DuckDB | `MarketDataProvider.get_daily_history()` + `load_dividends_dict()` |
| **Bar Chart Race (BCR)** | `GET /api/race-data` | DuckDB | `run_mars_simulation()` → `MarketDataProvider` |
| **Stock History** | `GET /api/stock/{id}/history` | DuckDB | `MarketDataProvider.get_daily_history()` + `load_dividends_dict()` |
| **Excel Export** | `GET /api/export/excel` | DuckDB | Shares `run_mars_simulation()` pipeline |
| **Portfolio History / Trend** | `GET /api/portfolio/trend` | DuckDB + SQLite | `_fetch_prices_from_market_cache()` → `MarketDataProvider.get_monthly_closes()` |
| **Portfolio Race Data** | `GET /api/portfolio/race-data` | DuckDB + SQLite | `_fetch_prices_from_market_cache()` → `MarketDataProvider` |
| **Portfolio Ladder** | `GET /api/portfolio/ladder` | DuckDB + yfinance | `get_portfolio_snapshot()` → `get_target_summary()` → `MarketDataProvider.get_latest_price()` |
| **Target Summary** | `GET /api/portfolio/targets/{id}/summary` | DuckDB + SQLite | `get_target_summary()` → `MarketDataProvider.get_latest_price()` + dividend fallback |
| **Admin Stats** | `GET /api/admin/market-data/stats` | DuckDB | `MarketDataProvider.get_stats()` |
| **Admin Refresh** | `POST /api/admin/refresh-market-data` | DuckDB | `MarketDataProvider.warm_latest_cache()` |

### ⚠️ yfinance Dependencies (Expected — Future Optimization)

| Feature | API Endpoint | Usage | Notes |
|---------|-------------|-------|-------|
| **Live Prices** | `GET /api/portfolio/prices` | Real-time stock prices (~30s delay) | Cannot replace with DuckDB (historical only) |
| **Dividend Sync** | `POST /sync/dividends`, `POST /sync/my-dividends` | Per-stock dividend fetch & cache | Uses `dividend_cache.py` → yfinance → file/SQLite. DuckDB write added but read still from cache |
| **Portfolio By-Type** | `GET /api/portfolio/by-type` | Live prices for snapshot | `fetch_live_prices()` → yfinance |

### ✅ External API Features (Expected)

| Feature | API Endpoint | Data Source | Notes |
|---------|-------------|-------------|-------|
| **CB Analysis** | `GET /api/cb/analyze`, `GET /api/cb/portfolio` | TWSE Bond API | `CBStrategy.analyze_list()` — no DuckDB needed |
| **AI Copilot** | `POST /api/chat` | Google Gemini API | LLM inference, context from portfolio data |
| **Stock Info** | Internal | TWSE ISIN HTML | `StockInfoService.fetch_stock_list()` → CSV cache |

### ✅ SQLite Features (User-Specific Data — Expected)

| Feature | API Endpoints | Notes |
|---------|-------------|-------|
| **Portfolio CRUD** | Groups, Targets, Transactions | User data stays in SQLite (separate concern) |
| **Leaderboard** | `GET /api/leaderboard` | Cached stats in SQLite |
| **Dividend Records** | `GET /api/portfolio/dividends/total` | `transaction_repo.get_dividend_history()` |
| **User Profile** | `GET/PUT /api/user/profile` | Auth data in SQLite |
| **Notifications** | Push notification engine | `RuthlessManager` operates on SQLite |

### 🧹 Legacy Dead Code (Candidate for Removal)

| Item | File | Status | Impact |
|------|------|--------|--------|
| `MarketCache` class | `app/services/market_cache.py` | **NOT referenced** by any active data path | Can be deleted. Was replaced by `MarketDataProvider`. |

**Note:** `MarketCache` is mentioned in a comment in `strategy_service.py:261` ("Prefer MarketCache Stock Price if YF failed") and as a docstring in `routers/strategy.py:24`, but these are **comments-only**, not code references. The class itself is dead code.

---

## Cash Ladder Tab — Audit Result

The Cash Ladder feature is exposed via:
- `GET /api/portfolio/ladder` → `calculation_service.get_portfolio_ladder()` → `get_portfolio_snapshot()`

**Data sources:**
1. **SQLite**: User targets, transactions, dividends
2. **yfinance**: Live prices via `fetch_live_prices()` (for current market value)
3. **DuckDB**: `MarketDataProvider.get_latest_price()` as fallback in `get_target_summary()`

**Verdict:** ✅ Uses DuckDB as fallback. Primary price source is yfinance (real-time), which is correct for a live portfolio view.

---

## Risk Matrix

| Risk | Level | Feature Affected | Mitigation |
|------|-------|-----------------|------------|
| DuckDB `dividends` table empty | Medium | Mars, BCR, Compound Interest, Stock History | Run `reimport_twse_dividends.py` after rebuild |
| `dividend_cache` reads from file/SQLite not DuckDB | Low | Portfolio Trend, Dividend History | Future optimization — current data is correct (yfinance sync) |
| `MarketCache` class accidentally invoked | Very Low | None currently | Delete the class to prevent confusion |
| yfinance rate limits on live prices | Low | Portfolio By-Type, Ladder | Existing 2-day fetch window is efficient |

---

## Recommendations

1. **Immediate**: Delete `app/services/market_cache.py` (dead code cleanup)
2. **Post-Rebuild**: Run `fill_rebuild_gaps.py` → `reimport_twse_dividends.py`
3. **Future**: Migrate `dividend_cache.py` reads to DuckDB to eliminate yfinance dependency for dividend data
4. **Future**: Add DuckDB-powered "last close price" API to replace yfinance for non-real-time price needs
