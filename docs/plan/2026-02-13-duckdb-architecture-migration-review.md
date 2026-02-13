# Plan Review: DuckDB Architecture Migration
**Date:** 2026-02-13
**Reviewers:** Primary Designer, Skeptic, Constraint Guardian, User Advocate, Integrator

---

## Phase 1 — Primary Designer Summary

The plan replaces 113 JSON files (2.7GB in-memory) with a single DuckDB file (~50MB RAM). 11 tasks across 5 phases. Key changes:
- New `MarketDataProvider` class replaces `MarketCache`
- `backfill_all_stocks()` writes to DuckDB instead of JSON
- All tabs (Trend, Race, Mars, CB, Portfolio) updated to use DuckDB queries
- Crons auto-aligned since they call `backfill_all_stocks()`

---

## Phase 2 — Structured Review

### 2️⃣ Skeptic / Challenger Agent

**Objection 1: DuckDB Concurrency**
> DuckDB is designed for OLAP workloads, NOT concurrent web serving. If 10 users hit `/api/trend` simultaneously, DuckDB's write lock could cause timeouts.

**Resolution:** DuckDB supports multiple concurrent *readers*. Writes (backfill) are rare (cron-only). We'll use `read_only=True` connections for the API layer and a single write connection for backfill. This is standard DuckDB usage pattern.

**Objection 2: Migration Data Loss**
> What if the migration script misparses a JSON file? We lose historical data.

**Resolution:** Plan explicitly states "Do NOT delete JSON files until Task 10 verification passes 100%." Migration script must include row-count validation against JSON source counts.

**Objection 3: Zeabur Persistent Storage**
> If Zeabur redeploys the container, the `.duckdb` file could be wiped.

**Resolution:** Critical risk. Options:
- **A)** Use Zeabur Volume Mount (attach persistent disk to `/app/data/`)
- **B)** Rebuild DuckDB from backfill on each deploy (slow but reliable)
- **C)** Store `.duckdb` in Git LFS (not ideal for write-heavy DBs)
- **Decision:** Use **Option A** (Volume Mount). If unavailable, fall back to **B** with a fast bootstrap script.

**Objection 4: DuckDB file size on disk**
> 2500 stocks × 250 days × 26 years × 7 columns = ~110M rows. How big is the file?

**Resolution:** DuckDB uses columnar compression. Estimated: 110M rows × ~50 bytes/row uncompressed = ~5.5GB. With DuckDB compression (typically 5-10x): **~550MB-1.1GB on disk**. This fits in Zeabur storage but is larger than the JSON files. Trade-off: disk space for RAM efficiency. Acceptable.

---

### 3️⃣ Constraint Guardian Agent

**Constraint 1: 512MB RAM Limit**
> DuckDB engine itself uses ~50MB. Query buffers for complex analytics could use more. Is total < 512MB?

**Analysis:**
- DuckDB engine: ~50MB
- FastAPI + uvicorn: ~30MB
- Python runtime: ~20MB
- Query buffer for Mars Strategy (5000 rows): ~0.5MB
- Dashboard price cache: ~0.2MB
- **Total: ~100MB** (well within 512MB limit ✅)

**Constraint 2: Startup Time**
> Current startup loads JSONs (30-60s on cloud). DuckDB startup should be faster.

**Analysis:** DuckDB opens a file handle, no data loading needed. Startup: <1 second. The `warm_latest_cache()` call queries latest prices for ~2500 stocks: ~2-5 seconds. **Massive improvement** from 30-60s to <5s. ✅

**Constraint 3: DuckDB Version Pinning**
> DuckDB is actively developed. File format changes between versions.

**Resolution:** Pin `duckdb>=1.0.0,<2.0.0` in `pyproject.toml`. DuckDB 1.x guarantees backward-compatible file format.

---

### 4️⃣ User Advocate Agent

**Concern 1: Will Tabs Feel Different?**
> End users should not notice any change except speed improvements.

**Analysis:** All data flows through the same API endpoints. Response shapes are identical. Users will notice:
- **Faster load times** (DuckDB queries vs JSON scan)
- **Accurate Volatility** in Mars Strategy (previously smoothed with monthly data)
- **No change** in Compound Interest, MoneyCome, or Portfolio tabs

**Concern 2: Admin Operations**
> Admin "Rebuild & Push" button — does it still work?

**Resolution:** The existing `/api/admin/system/initialize` endpoint must be updated to call `MarketDataProvider.warm_latest_cache()` instead of `MarketCache.get_prices_db()`. The backfill button continues to work since it calls `backfill_all_stocks()` which we're rewriting to target DuckDB.

**Concern 3: Data Freshness**
> If crons write to DuckDB, do users see stale data?

**Resolution:** DuckDB queries always return the latest committed data. No stale reads. The tiny in-memory cache for "latest prices" auto-expires after 5 minutes or on manual refresh.

---

## Phase 3 — Integration & Arbitration

### 5️⃣ Integrator / Arbiter Agent

**Decision Log:**

| # | Decision | Alternatives Considered | Resolution |
|---|----------|------------------------|------------|
| 1 | Use DuckDB (not Parquet+Polars) | Parquet files + Polars/Pandas for queries | DuckDB is simpler (single file, SQL, no extra query engine). Parquet is a format, DuckDB is a database. |
| 2 | Keep SQLite for user data | Merge everything into DuckDB | SQLite is battle-tested for OLTP user data. DuckDB is OLAP-optimized for analytics. Separation of concerns. |
| 3 | Tiny in-memory cache for latest prices | No cache (all queries hit DuckDB) | Dashboard needs sub-10ms response for "current price". DuckDB query is ~5-20ms. Cache eliminates this. |
| 4 | Volume mount for Zeabur persistence | Git LFS / rebuilt on each deploy | Volume mount is the standard approach for persistent data. |
| 5 | Keep JSON files during migration | Delete immediately | Safety net against migration bugs. Delete after verification. |

**Unresolved Objections:** None. All objections have been addressed.

**Final Disposition:** ✅ **APPROVED**

The plan is comprehensive, addresses all known risks, and provides a clear migration path. The 5-phase approach allows incremental verification. The "keep JSONs until verified" safety net is critical.

---

## Recommendations for Execution

1. **Branch Strategy**: Create `feat/duckdb-migration` branch. Merge to `master` only after Phase E verification passes.
2. **Parallel Development**: Phases A-B can be developed first. Phase C requires A-B. Phase D requires B. Phase E requires all.
3. **Rollback Plan**: If DuckDB causes unexpected issues on Zeabur, revert to JSON-based `MarketCache` (code still exists until Phase E cleanup).
4. **Estimated Effort**: 2-3 days for a focused developer.
