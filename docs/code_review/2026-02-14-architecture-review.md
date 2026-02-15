# Code Review: DuckDB Migration & Mars Strategy Optimization

**Status**: ⚠️ CAUTION (Architectural Risks Identified)
**Reviewer**: `[CV]` (Lead Auditor)
**Date**: 2026-02-14

## Executive Summary
The migration to DuckDB correctly resolves the N+1 query performance bottleneck, reducing Mars Strategy loading time from minutes to ~36s. However, the current "bulk-loading" strategy introduces a high risk of **Out of Memory (OOM)** crashes on cloud environments (Zeabur) as the database grows.

---

## 1. DuckDB Integration & Scalability
**Files**: `market_db.py`, `market_data_provider.py`

| Risk | Finding | Recommendation |
|------|---------|----------------|
| **OOM (High)** | `get_all_daily_history_df` loads the entire `daily_prices` table into RAM. At 11M+ rows, this will exceed 1GB+ RAM. | Use DuckDB's native aggregation (Window functions) in SQL instead of fetching raw rows for Python-level processing. |
| **Concurrency**| DuckDB only allows one writer. Background cron jobs might lock the web server. | Ensure `Backfill` scripts use `timeout` or separate read-only/write-out stages. |
| **Indexing** | No explicit indexes on `date` or `year`. | Add indexes to `daily_prices(date)` to optimize range queries. |

---

## 2. Mars Strategy Logic
**Files**: `strategy_service.py`, `roi_calculator.py`

| Risk | Finding | Recommendation |
|------|---------|----------------|
| **Precision** | `ROICalculator` triggers `RuntimeWarning: invalid value in scalar power` when cost is 0. | Add guard clauses: `if total_invested_cash <= 0: return 0.0`. |
| **Logic** | `end_year = 2025` is hardcoded in `MarsStrategy`. | Change to `datetime.now().year`. |
| **Efficiency** | `yearly_agg_groups` iteration is Python-heavy. | Consider moving split-adjusted CAGR calculation into a DuckDB custom aggregation or SQL macro. |

---

## 3. System & API Health
**File**: `app/main.py`

| Risk | Finding | Recommendation |
|------|---------|----------------|
| **Memory Leak**| `SIM_CACHE` is an unbounded global dict. Indefinite growth with unique params. | Replace with `cachetools.TTLCache` or `LRUCache`. |
| **Redundancy** | Excel name-enrichment runs on every request. | Pre-load the `name_map` into a class attribute at startup. |

---

## 4. Frontend Implementation
**File**: `MarsPage.tsx`

| Risk | Finding | Recommendation |
|------|---------|----------------|
| **State Bloat**| Holds 2,300+ objects in `stocks` state. | Virtualize the table if UI responsiveness drops, though 2.3k is currently manageable. |

---

## Overall Verdict
The implementation is a massive performance win for the current scale (~2k stocks, ~2M rows). However, the **architecture is not yet "Full Universe Ready"** (11M+ rows) due to memory constraints.

> [!IMPORTANT]
> **Priority 1**: Fix simulation `RuntimeWarning` in `ROICalculator`.
> **Priority 2**: Limit `SIM_CACHE` size in `app/main.py`.
