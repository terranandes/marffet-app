# Post-DuckDB Full System Verification — Implementation Plan

> **For BOSS (Terran):** This plan requires interactive review at each Gate. No phase proceeds without explicit GO from BOSS. 謹慎 — we verify everything.

**Goal:** Systematically verify that the DuckDB migration introduced zero data regressions, zero UI breakage, and zero operational issues across all 8 tabs, all API endpoints, all cron jobs, and the Zeabur deployment.

**Architecture:** 5-phase verification with BOSS interaction gates. Each phase has automated pre-checks and manual BOSS review. Any failure → STOP, file JIRA bug, fix, re-verify.

**Tech Stack:** Python 3.12, DuckDB, FastAPI, Playwright (browser tests), pytest

---

## User Review Required

> [!IMPORTANT]
> This plan is designed to be **interactive** — BOSS reviews each phase before proceeding.
> Each Gate requires BOSS to visually confirm data accuracy on real screens.

> [!WARNING]
> `market_cache.py` (11KB) still exists on disk. Must confirm it's dead code before deletion.
> DuckDB date range shows `2026-12-31` which needs investigation (likely yearly summary artifacts).

---

## Phase 1: Backend Health Check (Automated)

**Objective:** Confirm the server starts cleanly, DuckDB schema is intact, and all services initialize without errors.

### Task 1.1: Dead Code Scan

**What:** Grep the entire codebase for any remaining references to `MarketCache` or `market_cache`.

**Steps:**
```bash
# From project root
grep -rn "MarketCache\|market_cache" app/ scripts/ tests/ --include="*.py" | grep -v "__pycache__" | grep -v ".pyc"
```

**Expected:** Only `app/services/market_cache.py` itself appears (if any other file imports it → 🔴 STOP).

**GO/NO-GO:** If zero external references → safe to delete. If references found → fix before continuing.

---

### Task 1.2: Server Startup Test

**What:** Start the FastAPI backend and verify it boots without errors in < 5 seconds.

**Steps:**
```bash
cd /home/terwu01/github/martian

# Start backend
timeout 10 uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info 2>&1 | head -20
```

**Expected:** "Uvicorn running on http://0.0.0.0:8000" appears. No ImportError, no DuckDB errors.

---

### Task 1.3: DuckDB Integrity Check

**What:** Verify DuckDB stats match expectations.

**Steps:**
```bash
uv run python scripts/ops/duckdb_stats.py
```

**Expected:**
- Price Rows: ~6.5M
- Dividend Rows: ~33K
- Stock Rows: ~51K
- Date Range: 2000-01-03 to 2026-02-xx (investigate if upper bound is 2026-12-31)
- Distinct Stocks: ~2,300+

**Additional Deep Check:**
```bash
uv run python -c "
import duckdb
c = duckdb.connect('data/market.duckdb', read_only=True)
# Check actual latest daily date (not yearly summary)
r = c.execute(\"SELECT MAX(date) FROM daily_prices WHERE date < '2026-06-01'\").fetchone()
print(f'Latest real daily date: {r[0]}')
# Check for NaN prices
r2 = c.execute('SELECT COUNT(*) FROM daily_prices WHERE close IS NULL OR close = 0').fetchone()
print(f'Null/zero close prices: {r2[0]}')
c.close()
"
```

---

### Task 1.4: Unit Test Suite

**What:** Run all existing unit tests.

**Steps:**
```bash
uv run pytest tests/unit/ -v --tb=short 2>&1 | tail -30
```

**Expected:** All tests pass. No DuckDB connection errors.

---

### Task 1.5: Integration Test Suite (API-level)

**What:** Run `test_all_tabs.py` against local backend.

**Prerequisites:** Backend running on port 8000, Frontend running on port 3000.

**Steps:**
```bash
# Terminal 1: Start backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Terminal 2: Start frontend
cd project_tw && bun run dev &

# Terminal 3: Run tests
uv run pytest tests/integration/test_all_tabs.py -v --tb=short
```

**Expected:** All 8 tab test classes pass (Mars, Race, Compound, CB, Portfolio, Trend, MyRace, CashLadder).

---

### 🚪 GATE 1: BOSS Review

**BOSS Action:** Review Phase 1 terminal output.
- Are all unit tests green?
- Are all integration tests green?
- Is the dead code scan clean?
- DuckDB stats look reasonable?

**Decision:** GO → Phase 2 | NO-GO → Fix issues first.

---

## Phase 2: API Endpoint Deep Verification

**Objective:** Verify every API endpoint returns correct data shapes and values.

### Task 2.1: Mars Strategy API

**What:** Call `/api/strategy/mars/analyze` and verify CAGR/Volatility for benchmark stocks.

**Steps:**
```bash
# TSMC (2330) - Expected CAGR ~19% from 2006
curl -s -X POST http://localhost:8000/api/strategy/mars/analyze \
  -H "Content-Type: application/json" \
  -d '{"start_year": 2006, "stock_ids": ["2330"]}' | python -m json.tool | head -30

# 0050 (ETF) - Expected CAGR >10% (split-adjusted)
curl -s -X POST http://localhost:8000/api/strategy/mars/analyze \
  -H "Content-Type: application/json" \
  -d '{"start_year": 2006, "stock_ids": ["0050"]}' | python -m json.tool | head -30
```

**Verification Criteria (BOSS confirms):**
| Stock | Metric | Expected Range | If Outside → |
|-------|--------|---------------|-------------|
| 2330 | CAGR | 15-25% | 🔴 Data issue |
| 2330 | Volatility | 25-40% | 🟡 Check daily data count |
| 0050 | CAGR | 8-15% | 🔴 Split adjustment issue |

---

### Task 2.2: Race Data API

**What:** Verify monthly closes for Race animation.

**Steps:**
```bash
# Check if race-data endpoint returns data (requires auth)
curl -s http://localhost:8000/api/portfolio/race-data \
  -H "Authorization: Bearer <BOSS_TOKEN>" | python -m json.tool | head -30
```

**If auth required:** BOSS tests via the UI in Phase 3.

---

### Task 2.3: Admin Stats API

**What:** Verify `/api/admin/market-data/stats` returns correct DuckDB stats.

**Steps:**
```bash
curl -s http://localhost:8000/api/admin/market-data/stats \
  -H "Authorization: Bearer <ADMIN_TOKEN>" | python -m json.tool
```

**Expected:** JSON with `price_rows`, `dividend_rows`, `stock_rows`, `min_date`, `max_date`, `distinct_stocks_prices`.

---

### Task 2.4: Portfolio Dividends API

**What:** Verify dividend totals for a known user.

**Steps:** BOSS tests via UI (Phase 3).

---

### 🚪 GATE 2: BOSS Review

**BOSS Action:**
- Verify TSMC CAGR is in 15-25% range
- Verify 0050 CAGR is in 8-15% range (split-adjusted)
- Confirm Volatility numbers are daily-based (not monthly approximation)

**Decision:** GO → Phase 3 | NO-GO → Investigate data accuracy.

---

## Phase 3: UI Tab-by-Tab Visual Verification (Browser)

**Objective:** Open each tab in the browser and visually verify data, charts, and interactions.

> [!IMPORTANT]
> This phase requires BOSS to review screenshots/recordings of each tab.
> Agent will open the browser and capture evidence for BOSS review.

### Task 3.1: Mars Strategy Tab (`/mars`)

**Steps:**
1. Navigate to `http://localhost:3000/mars`
2. Run analysis with default settings (start_year=2006)
3. Verify: Table populates with stock rows
4. Verify: CAGR column shows reasonable values (not all 0% or NaN)
5. Verify: Click TSMC (2330) → detail page shows BAO/BAH/BAL charts
6. Screenshot evidence

---

### Task 3.2: Bar Chart Race Tab (`/race`)

**Steps:**
1. Navigate to `http://localhost:3000/race`
2. Verify: Animation loads with stock bars
3. Verify: Year counter advances smoothly (2000 → 2026)
4. Verify: No gaps, no frozen frames, no NaN labels
5. Screenshot evidence

---

### Task 3.3: Compound Interest Tab (`/compound`)

**Steps:**
1. Navigate to `http://localhost:3000/compound`
2. Verify: Page loads (iframe content visible)
3. Screenshot evidence

---

### Task 3.4: CB Strategy Tab (`/cb`)

**Steps:**
1. Navigate to `http://localhost:3000/cb`
2. Verify: CB data loads or appropriate empty state
3. Screenshot evidence

---

### Task 3.5: Portfolio Tab (`/portfolio`)

**Steps:**
1. Navigate to `http://localhost:3000/portfolio`
2. **Guest Mode:** Verify group creation, stock addition, transaction works
3. **Logged In (BOSS):** Verify real portfolio shows correct market values
4. Verify: Dividend totals match expectations
5. Screenshot evidence

---

### Task 3.6: Trend Tab (`/trend`)

**Steps:**
1. Navigate to `http://localhost:3000/trend`
2. Verify: Portfolio value chart renders
3. Verify: Date range is reasonable
4. Screenshot evidence

---

### Task 3.7: My Race Tab (`/myrace`)

**Steps:**
1. Navigate to `http://localhost:3000/myrace`
2. Verify: Personal race animation loads
3. Screenshot evidence

---

### Task 3.8: Cash Ladder Tab (`/ladder`)

**Steps:**
1. Navigate to `http://localhost:3000/ladder`
2. Verify: Leaderboard renders
3. Screenshot evidence

---

### 🚪 GATE 3: BOSS Visual Review

**BOSS Action:**
- Review all 8 tab screenshots
- Confirm Mars numbers match expectations
- Confirm Portfolio values match BOSS's real portfolio
- Flag any visual anomalies

**Decision:** GO → Phase 4 | NO-GO → File JIRA, fix UI issues.

---

## Phase 4: Cron & Ops Verification

**Objective:** Verify cron scripts work correctly with DuckDB.

### Task 4.1: Supplement Prices Dry Run

**Steps:**
```bash
# Run supplement_prices in dry mode (limit to 2 stocks)
uv run python scripts/cron/supplement_prices.py 2>&1 | head -20
```

**Expected:** Script runs without error, updates DuckDB rows.

---

### Task 4.2: DuckDB Stats Health Check

**Steps:**
```bash
uv run python scripts/ops/duckdb_stats.py
```

**Expected:** Row counts unchanged or slightly increased (if supplement added data).

---

### Task 4.3: Verify Integrity Script

**Steps:**
```bash
uv run python scripts/ops/verify_integrity.py 2>&1 | tail -20
```

**Expected:** Pass with no critical gaps flagged.

---

### 🚪 GATE 4: BOSS Review

**BOSS Action:**
- Confirm cron scripts run cleanly
- Confirm DuckDB stats are stable after ops operations

**Decision:** GO → Phase 5 | NO-GO → Fix ops scripts.

---

## Phase 5: Zeabur Deployment & Production Soak

**Objective:** Deploy to Zeabur and monitor for 24 hours.

### Task 5.1: Zeabur Volume Configuration

**BOSS Action Required:**
1. Go to Zeabur Dashboard → Martian Service → Storage
2. Add persistent volume: Mount path = `/app/data/`, Size = 1GB
3. Verify `market.duckdb` persists across container restarts

---

### Task 5.2: Deploy to Zeabur

**Steps:**
```bash
git push origin master
```

Monitor Zeabur build logs for success.

---

### Task 5.3: Production Smoke Test

**BOSS Action:**
1. Open production URL
2. Check Mars Strategy tab → TSMC CAGR matches local
3. Check Portfolio tab → Real portfolio values correct
4. Check Admin panel → DuckDB stats endpoint responds

---

### Task 5.4: 24h Soak Test

**Monitor for 24 hours:**
- No OOM restarts (Zeabur container metrics)
- Crons execute on schedule
- API response times < 500ms

---

### 🚪 GATE 5: Final Sign-Off

**BOSS Action:**
- Confirm 24h soak passed
- Confirm no OOM restarts
- Confirm all tabs functional in production

**Decision:** ✅ VERIFIED → Phase 8 begins | ❌ ISSUES → Hotfix cycle.

---

## Verification Commands Quick Reference

| Test | Command | Expected |
|------|---------|----------|
| Dead code scan | `grep -rn "MarketCache\|market_cache" app/ scripts/ tests/ --include="*.py" \| grep -v __pycache__` | Only market_cache.py itself |
| Server start | `uv run uvicorn app.main:app --port 8000` | Boots in < 5s |
| DuckDB stats | `uv run python scripts/ops/duckdb_stats.py` | 6.5M prices, 33K divs |
| Unit tests | `uv run pytest tests/unit/ -v --tb=short` | All pass |
| Integration tests | `uv run pytest tests/integration/test_all_tabs.py -v` | All pass |
| Mars analyze | `curl -X POST .../mars/analyze -d '{"start_year":2006,"stock_ids":["2330"]}'` | CAGR ~19% |
| E2E suite | `uv run python tests/e2e/e2e_suite.py` | All pass |

---

## Preserved (DO NOT TOUCH)

| File | Purpose |
|------|---------|
| `data/portfolio.db` | User accounts, portfolios, transactions |
| `data/dividend_patches.json` | Manual dividend overrides |
| `app/auth.py` | Authentication |
| `app/routers/user.py` | User management |
