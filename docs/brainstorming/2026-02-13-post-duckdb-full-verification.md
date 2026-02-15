# Brainstorming: Post-DuckDB Full System Verification

**Date:** 2026-02-13
**Participants:** `[PL]` Lead, `[CV]` Skeptic, `[CODE]` Constraint Guardian, `[UI]` User Advocate

---

## Context

DuckDB migration (Phase 7) is merged to `master`. 6.5M price rows, 33K dividends, 51K stocks now reside in `data/market.duckdb` (295MB). The old JSON engine (2.7GB RAM) has been deleted. **This verification must ensure zero data regressions before production stability is declared.**

BOSS指示: 需要 **謹慎** — every tab, every function, with interactive checkpoints.

---

## Scope: What Needs Verification

### 8 Frontend Tabs

| # | Tab | Route | Data Source | Risk Level |
|---|-----|-------|-------------|------------|
| 1 | Mars Strategy | `/mars` | `MarketDataProvider.get_daily_history()` | 🔴 HIGH |
| 2 | Bar Chart Race | `/race` | `MarketDataProvider.get_monthly_closes()` | 🟡 MEDIUM |
| 3 | Compound Interest | `/compound` | Static iframe | 🟢 LOW |
| 4 | CB Strategy | `/cb` | `MarketDataProvider.get_latest_price()` | 🟡 MEDIUM |
| 5 | Portfolio | `/portfolio` | `get_latest_price()` + `portfolio.db` | 🔴 HIGH |
| 6 | Trend | `/trend` | `get_portfolio_history()` | 🟡 MEDIUM |
| 7 | My Race | `/myrace` | `get_portfolio_race_data()` | 🟡 MEDIUM |
| 8 | Cash Ladder | `/ladder` | `get_portfolio_ladder()` | 🟢 LOW |

### Backend Services

| Service | Changed? | Risk |
|---------|----------|------|
| `market_data_provider.py` | NEW | 🔴 Core data layer |
| `calculation_service.py` | MODIFIED | 🔴 All calculations |
| `strategy_service.py` | MODIFIED | 🔴 Mars/CB |
| `market_data_service.py` | MODIFIED | 🟡 Backfill pipeline |
| `roi_calculator.py` | MODIFIED | 🟡 ROI/dividend |
| `dividend_cache.py` | MODIFIED | 🟡 Dividend sync |

### Ops & Cron

| Script | Status | Risk |
|--------|--------|------|
| `supplement_prices.py` | Rewritten | 🟡 |
| `annual_prewarm.sh` | Updated | 🟢 |
| `duckdb_stats.py` | NEW | 🟢 |
| `verify_integrity.py` | Updated | 🟢 |

---

## Risk Analysis

### 🔴 Risk 1: Data Accuracy Regression
Daily data replaced monthly approximations. Any off-by-one in date parsing, missing years, or incorrect aggregation would silently corrupt CAGR/Volatility.
**Mitigation:** BOSS manually verifies known benchmarks (TSMC, 0050, 0056).

### 🔴 Risk 2: race_cache Deletion
Old `race_cache` dropped from `portfolio.db`. Race/MyRace tabs now rely on DuckDB `get_monthly_closes()`. Edge cases: delistings, IPOs mid-year, stocks with gaps.
**Mitigation:** Run race for known stocks and compare curve shape.

### 🟡 Risk 3: Legacy market_cache.py Still on Disk
File exists (11KB) but should be dead code. Hidden imports = runtime crash.
**Mitigation:** Grep all imports before declaring it dead.

### 🟡 Risk 4: DuckDB Date Range Anomaly
Stats show date range `2000-01-03 to 2026-12-31`. The `2026-12-31` upper bound is suspicious for Feb 2026 data — likely from yearly summaries in the migration script.
**Mitigation:** Query actual MAX date for daily rows only.

### 🔴 Risk 5: Zeabur Volume Persistence
`market.duckdb` (295MB) needs persistent volume. Without it, every container restart = data loss.
**Mitigation:** BOSS configures Zeabur volume mount, we verify via restart test.

---

## Multi-Agent Review

### `[CV]` Skeptic
- "What if market_cache.py is still imported somewhere?" → Must grep ALL references.
- "The 2026-12-31 date is wrong." → Verify actual latest daily date.
- "Concurrent cron + web request could cause DuckDB lock?" → Stress test needed.

### `[CODE]` Constraint Guardian
- Startup must be < 5s. Verify with timer.
- API response < 500ms for Mars analyze. Verify with curl.
- RSS < 200MB under load. Verify with `resource.getrusage`.
- Admin endpoints still require auth. Verify with unauthenticated request.

### `[UI]` User Advocate
- Users care about: correct portfolio values, accurate CAGR rankings, smooth Race animation.
- Users will notice: wrong prices, missing dividends, slow page loads, broken charts.
- Must verify on both Desktop and Mobile viewports.

### `[PL]` Integrator Decision
**APPROVED.** Plan will use 5 phases with explicit BOSS gates. Each phase has automated pre-checks + manual BOSS review with GO/NO-GO criteria.

---

## Decision Log

| # | Decision | Alternatives | Rationale |
|---|----------|-------------|-----------|
| 1 | 5-phase plan with BOSS gates | Full automation only | BOSS wants interactive 謹慎 verification |
| 2 | Local-first, then Zeabur | Deploy-first | Avoid production incidents |
| 3 | Keep market_cache.py until grep confirms dead | Delete immediately | Safety net in case of hidden dependency |
| 4 | Visual browser verification for UI tabs | API-only tests | Data accuracy needs human eyes on real UI |
