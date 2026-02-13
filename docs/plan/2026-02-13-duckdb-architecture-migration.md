# DuckDB Architecture Migration — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace JSON-based `MarketCache` (2.7GB RAM) with DuckDB columnar storage (~50MB RAM) to permanently solve Zeabur OOM crashes while enabling accurate daily-level analytics.

**Architecture:** All market price & dividend data moves from `data/raw/*.json` files + `race_cache` SQLite into a single `data/market.duckdb` file. A new `MarketDataProvider` abstraction replaces `MarketCache` as the single data access layer. User data (`portfolio.db`) is untouched.

**Tech Stack:** Python 3.12, DuckDB (pip), FastAPI, yfinance, pandas

---

## Impact Matrix

| Component | Current Source | New Source | Effort |
|-----------|---------------|-----------|--------|
| Dashboard (latest price) | `MarketCache` RAM | DuckDB + tiny in-mem cache | Low |
| Trend (monthly portfolio value) | `MarketCache` | DuckDB query | Medium |
| Race (bar chart race) | `race_cache` SQLite | DuckDB query | Medium |
| Mars Strategy (20yr CAGR+Vol) | Hybrid RAM+SQLite | DuckDB daily query | **High** |
| CB Strategy (latest price) | `MarketCache` RAM | DuckDB + cache | Low |
| Portfolio (summary) | `MarketCache` + dividend_cache | DuckDB | Medium |
| Backfill Writer | JSON files | DuckDB INSERT | **High** |
| Crons | Shell → backfill | Same (auto-aligned) | Low |
| Admin UI | JSON stats | DuckDB stats | Medium |

---

## Phase A: Foundation (DuckDB Setup + Migration Script)

### Task 1: Install DuckDB & Create Schema

**Files:**
- Modify: `pyproject.toml` (add `duckdb` dependency)
- Create: `app/services/market_db.py` (new DuckDB engine)
- Test: `tests/unit/test_market_db.py`

**Step 1: Add dependency**
```bash
uv add duckdb
```

**Step 2: Create `market_db.py`**
```python
# app/services/market_db.py
import duckdb
from pathlib import Path

DB_PATH = Path("data/market.duckdb")

def get_market_db():
    """Get a DuckDB connection. Thread-safe: each call returns a new connection."""
    return duckdb.connect(str(DB_PATH), read_only=False)

def init_schema():
    """Create tables if they don't exist."""
    with get_market_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_prices (
                stock_id VARCHAR,
                date DATE,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume BIGINT,
                market VARCHAR DEFAULT 'TWSE',
                PRIMARY KEY (stock_id, date)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dividends (
                stock_id VARCHAR,
                year INTEGER,
                cash_dividend DOUBLE DEFAULT 0,
                stock_dividend DOUBLE DEFAULT 0,
                PRIMARY KEY (stock_id, year)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                stock_id VARCHAR PRIMARY KEY,
                name VARCHAR,
                market_type VARCHAR,
                industry VARCHAR
            )
        """)
```

**Step 3: Write unit test**
```python
# tests/unit/test_market_db.py
def test_schema_creation():
    from app.services.market_db import init_schema, get_market_db
    init_schema()
    with get_market_db() as conn:
        tables = conn.execute("SHOW TABLES").fetchall()
        assert len(tables) >= 3
```

**Step 4: Run test, verify pass**
```bash
uv run pytest tests/unit/test_market_db.py -v
```

**Step 5: Commit**
```bash
git add . && git commit -m "feat(duckdb): add DuckDB engine with schema"
```

---

### Task 2: JSON → DuckDB Migration Script

**Files:**
- Create: `scripts/ops/migrate_json_to_duckdb.py`
- Test: Manual verification (count rows)

**Step 1: Write migration script**
```python
# scripts/ops/migrate_json_to_duckdb.py
"""
One-time migration: Read all data/raw/*.json → INSERT into data/market.duckdb
Handles: Market_{Year}_Prices.json, TPEx_Market_{Year}_Prices.json, TWSE_Dividends_{Year}.json
"""
import json, sys, duckdb
from pathlib import Path

def migrate():
    db = duckdb.connect("data/market.duckdb")
    # ... read each JSON, extract daily data, batch INSERT
    # ... read dividend JSON, batch INSERT
    # Report: total rows inserted, time taken
```

**Step 2: Run migration**
```bash
uv run scripts/ops/migrate_json_to_duckdb.py
```

**Step 3: Verify row counts**
```bash
uv run -c "import duckdb; c=duckdb.connect('data/market.duckdb'); print(c.execute('SELECT COUNT(*) FROM daily_prices').fetchone()); print(c.execute('SELECT COUNT(DISTINCT stock_id) FROM daily_prices').fetchone())"
```

**Step 4: Commit**
```bash
git add . && git commit -m "feat(duckdb): add JSON-to-DuckDB migration script"
```

---

## Phase B: Core Rewrite (MarketDataProvider)

### Task 3: Create MarketDataProvider (Read Layer)

**Files:**
- Create: `app/services/market_data_provider.py` (NEW)
- Test: `tests/unit/test_market_data_provider.py`

**Purpose:** Single abstraction for ALL market data reads. Replaces `MarketCache.get_stock_history_fast()`, `MarketCache.get_strategy_history()`, `MarketCache.get_prices_db()`, and all `race_cache` queries.

```python
# app/services/market_data_provider.py
class MarketDataProvider:
    """Unified market data access layer backed by DuckDB."""
    
    _latest_prices = {}  # Tiny in-memory cache: {stock_id: {date, close}}
    
    @classmethod
    def get_daily_history(cls, stock_id: str, start_date=None, end_date=None) -> list[dict]:
        """Full daily OHLCV for a stock. Used by Mars Strategy, ROICalculator."""
        
    @classmethod
    def get_latest_price(cls, stock_id: str) -> float:
        """Latest close price. Uses in-memory cache first, DuckDB fallback."""
        
    @classmethod
    def get_monthly_closes(cls, stock_ids: list, start_year: int) -> dict:
        """Month-end closes for Race/Trend. Replaces race_cache."""
        
    @classmethod
    def get_dividends(cls, stock_id: str, start_year: int = 2000) -> dict:
        """Dividend history for ROI calculation."""
        
    @classmethod
    def get_stock_list(cls) -> list[str]:
        """All known stock IDs."""
    
    @classmethod
    def warm_latest_cache(cls):
        """Load latest price for all stocks into RAM (~175KB)."""
```

**Step 1-5: Write test → Implement → Verify → Commit**

---

### Task 4: Rewrite Backfill Writer (Write Layer)

**Files:**
- Modify: `app/services/market_data_service.py` — Replace `_save_json_safe()` with DuckDB INSERT
- Modify: `backfill_all_stocks()` — Remove JSON file I/O, use DuckDB batch inserts
- Test: `tests/unit/test_backfill_duckdb.py`

**Key Changes:**
- Remove: `_save_json_safe()`, `_merge_data_dict()`
- Add: `_save_to_duckdb(stock_id, year, daily_data, dividends)`
- Remove: `flush_results()` (no more JSON buffering)
- DuckDB handles atomicity natively (ACID transactions)

**Step 1-5: Test → Implement → Verify → Commit**

---

## Phase C: Consumer Alignment (All Tabs)

### Task 5: Update Calculation Service (Trend + Race + Portfolio)

**Files:**
- Modify: `app/services/calculation_service.py`
  - `get_portfolio_history()` → Use `MarketDataProvider.get_daily_history()`
  - `get_portfolio_race_data()` → Use `MarketDataProvider.get_monthly_closes()`
  - `_fetch_prices_from_market_cache()` → Replace with `MarketDataProvider`
  - `get_target_summary()` → Use `MarketDataProvider.get_latest_price()`

**Step 1-5: Test → Implement → Verify → Commit**

---

### Task 6: Update Strategy Service (Mars + CB)

**Files:**
- Modify: `app/services/strategy_service.py`
  - `MarsStrategy.analyze()` → Use `MarketDataProvider.get_daily_history()`
  - `CBStrategy.analyze()` → Use `MarketDataProvider.get_latest_price()`
  - Remove: `MarketCache` import

**Step 1-5: Test → Implement → Verify → Commit**

---

### Task 7: Update Admin Router & Main

**Files:**
- Modify: `app/routers/admin.py`
  - `/api/admin/system/initialize` → Call `MarketDataProvider.warm_latest_cache()` instead of `MarketCache.get_prices_db()`
  - Add: `/api/admin/market-data/stats` → DuckDB row counts, file size
- Modify: `app/main.py`
  - `lifespan()` → Replace heavy `MarketCache.get_prices_db()` with lightweight `MarketDataProvider.warm_latest_cache()`
  - Remove: `start_year` logic, `IS_CLOUD` cache limiting (no longer needed)

**Step 1-5: Test → Implement → Verify → Commit**

---

## Phase D: Cron & Ops Revamp

### Task 8: Update Cron Scripts

**Files:**
- Modify: `scripts/cron/refresh_current_year.sh` → No change needed if it calls `backfill_all_stocks()`
- Modify: `scripts/cron/annual_prewarm.sh` → Verify it works with DuckDB writer
- Modify: `scripts/cron/quarterly_dividend_sync.sh` → Verify dividend sync writes to DuckDB
- Modify: `scripts/cron/supplement_prices.py` → Rewrite to patch DuckDB directly

**Step 1-5: Test each cron → Verify → Commit**

---

### Task 9: Update Ops Scripts

**Files:**
- Modify: `scripts/ops/verify_integrity.py` → Query DuckDB instead of JSON files
- Modify: `scripts/ops/patch_stock_data.py` → UPDATE DuckDB rows
- Delete: `scripts/ops/measure_memory.py` (no longer relevant)
- Delete: `scripts/ops/measure_sqlite_fetch.py` (no longer relevant)
- Create: `scripts/ops/duckdb_stats.py` → Quick DuckDB health check

**Step 1-5: Test → Implement → Verify → Commit**

---

## Phase E: Verification & Cleanup

### Task 10: Full System Verification

**Files:**
- Test: `tests/e2e/e2e_suite.py` (existing)
- Test: `tests/integration/test_all_tabs.py` (existing)
- Create: `scripts/ops/verify_migration.py` → Compare DuckDB vs JSON data

**Verification Checklist:**
1. TSMC (2330) CAGR from 2006: Should be ~19%
2. TSMC Volatility: Should now be calculated on ~5000 daily points (not 12 monthly)
3. Race data coverage: All 2500+ stocks, 2000-2026
4. Dashboard: Latest prices load in <100ms
5. Memory on simulated Cloud: `resource.getrusage` < 200MB
6. All crons produce expected output

**Step 1-5: Run tests → Fix issues → Re-verify → Commit**

---

### Task 11: Cleanup & Deploy

**Files:**
- Delete: `app/services/market_cache.py` (replaced by `market_data_provider.py`)
- Delete: `data/raw/Market_*_Prices.json` (data now in DuckDB)
- Delete: `data/raw/TPEx_Market_*_Prices.json`
- Delete: `data/raw/TWSE_Dividends_*.json`
- Modify: `.gitignore` → Add `data/market.duckdb` (too large for Git)
- Modify: `Dockerfile` → Ensure DuckDB is installed
- Remove: `race_cache` table from `portfolio.db`

> [!CAUTION]
> Do NOT delete JSON files until Task 10 verification passes 100%.

**Step 1: Deploy to Zeabur**
```bash
git add . && git commit -m "feat(duckdb): complete architecture migration" && git push origin master
```

**Step 2: Verify on Zeabur**
- Check memory usage via admin panel
- Run Mars Strategy on production
- Verify all tabs load

---

## Preserved (DO NOT TOUCH)

| File | Purpose |
|------|---------|
| `data/portfolio.db` | User accounts, portfolios, transactions, subscriptions |
| `data/dividend_patches.json` | Manual dividend overrides |
| `data/dividends_all.json` | Legacy fallback |
| `app/database.py` | SQLite connection for user data |
| `app/auth.py` | Authentication |
| `app/routers/user.py` | User management |
| `app/routers/portfolio.py` | Portfolio CRUD |
