# Code Review Note (Post-Deployment Evening Sync)
**Date:** 2026-02-22 18:42
**Reviewer:** [CV]

## 1. Scope
Reviewing 15 commits pushed to `master` during the Zeabur deployment session (commits `058db3a` → `c6dc181`). 35 files modified across `app/`, +752/-470 lines.

## 2. Critical Changes Reviewed

### `app/services/strategy_service.py` — Mars Chunked Streaming
- **Before:** `MarketDataProvider.get_all_daily_history_df(start_date)` loaded ALL 4.5M rows into a single Pandas DataFrame.
- **After:** DuckDB queried in 200-stock batches via parameterized SQL. Peak memory ~40MB.
- ✅ `conn` properly guarded in `try/finally` block
- ✅ `sanitize_numpy()` recursion covers `dict`, `list`, and `hasattr(obj, 'item')` patterns
- ⚠️ **Minor: Unused imports** — Lines 1-2 have commented-out `import pandas` / `import numpy` but these are imported later via `import numpy as np` and `import pandas as pd` inside the function body. Cosmetic only.

### `app/services/market_db.py` — DuckDB Path Resolution
- ✅ `_is_db_empty()` correctly treats exceptions as "empty" (safe fallback)
- ✅ `_rehydrate_from_parquet()` enforces `PRAGMA memory_limit='256MB'` and `threads=1`
- ⚠️ **Minor: Missing `try/finally`** in `_is_db_empty()` — if `conn.execute()` throws, `conn.close()` won't execute. Low risk since `read_only=True` connections don't hold write locks.
- ✅ `_resolve_db_path()` correctly purges empty shells via `unlink()` before rehydrating

### `app/services/market_data_provider.py` — ARGMAX Optimization
- ✅ Replaced `ROW_NUMBER() OVER(PARTITION BY ...)` with `ARGMAX(close, date)` — significantly reduces DuckDB memory overhead during cache warming

### `app/routers/strategy.py` — Debug Wrapper Cleanup
- ✅ Debug `json.dumps()` wrapper removed during this meeting
- ✅ Endpoint is now clean: `analyze → return results`

### `app/main.py` — Debug Flag Cleanup
- ✅ `debug=True` removed during this meeting
- Application restores to production-safe configuration

### `app/services/backup.py` — Parquet Git Integration
- ✅ `data/backup/*.parquet` added to git commit payload in `refresh_prewarm_data()`
- ✅ Uses `str(file_path)` for tree entry paths

## 3. DuckDB Connection Safety Audit
| File | Connection Pattern | Properly Closed? |
|------|-------------------|-----------------|
| `strategy_service.py` | `try/finally: conn.close()` | ✅ |
| `market_db.py` (`_rehydrate`) | `try/finally: conn.close()` | ✅ |
| `market_db.py` (`_is_db_empty`) | Sequential `conn.close()` | ⚠️ Minor risk |
| `market_db.py` (`get_connection`) | Returns `conn` (caller responsible) | ✅ By design |
| `market_data_provider.py` | `try/finally: conn.close()` | ✅ |

## 4. Verdict
- **No blockers.** The deployment is functionally correct and memory-safe.
- **Recommended follow-up:** Add `try/finally` to `_is_db_empty()` for connection safety.
- **Approval:** ✅ Code reviewed and approved for production.
