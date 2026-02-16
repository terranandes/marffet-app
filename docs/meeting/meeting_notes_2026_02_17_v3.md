# Martian Sync-Up Meeting 🛰️ (2026-02-17 v3)

**Date**: 2026-02-17
**Time**: 04:50 HKT
**Participants**: [PM], [SPEC], [PL], [CODE], [UI], [CV]
**Meeting Status**: Pre-Deployment Final Polish

## 1. Project Progress & Features
- **Mars Strategy Correlation**: Completed (80% match, < 12s cold start locally).
- **Core Performance**: 3.8x speedup achieved via numpy-based split detection and bulk data loading.
- **Zeabur Readiness**: 
  - Persistent volume path resolved to `/data/market.duckdb`.
  - Copy-on-startup logic implemented to migrate data from app bundle to persistent volume.
  - Admin endpoints created for DB backup/restore and local-to-cloud sync.
- **Data Refresh**: Nightly cron job updated to `period=2d` with one-day safety buffer.

## 2. Bug Triage & Fixes (Critical)
- **BUG-011: Export Excel Timeout**: 
  - **Status**: ✅ FIXED.
  - **Issue**: API was re-running the 5-minute per-stock simulation loop for 1,629 stocks.
  - **Fix**: Rewrote `/api/export/excel` to reuse `SIM_CACHE` or use the fast bulk simulation logic.
- **BUG-012: Manual Detail Multi-Year Bogus Data**:
  - **Status**: ✅ FIXED.
  - **Issue**: TSMC showed "4923 Years" in the detail modal.
  - **Reason**: Code used `len(df_group)` (daily price rows) instead of year count. Fix: used yearly stats length.
- **BUG-013: BCR Tab Loading Speed**:
  - **Status**: ✅ FIXED.
  - **Issue**: Same as Export, was using slow legacy loop. Rewritten to use high-performance logic.

## 3. Findings & Discrepancies
- **Price Data Range (2000 vs 2004)**:
  - **Observation**: BOSS correctly noted dividends start at 2000, but DuckDB prices start at 2004-01-29.
  - **Investigation**: Verified `yfinance` **does** have data since 2000 (e.g., 2330.TW).
  - **Triage**: Current DuckDB was likely backfilled with a script lacking the 2000-2004 window.
  - **Action**: Planned a "Deep Backfill (2000-2004)" for all stocks to fill the gap.

## 4. Deployment Plan (Zeabur - 2026-02-18)
- **Phase 1**: Push code changes to `master`.
- **Phase 2**: Use `POST /api/admin/upload/duckdb` to upload the 1.1GB local database directly to Zeabur's persistent volume.
- **Phase 3**: Verify persistent volume mounting and data availability via `/api/debug/cache-info`.
- **Phase 4**: Run full test flow on Zeabur.

## 5. Action Items
- [PL] Coordinate "Deep Backfill (2000-2004)" task once local speed is verified.
- [CV] Final logic check on split detection for pre-2004 adjusted prices.
- [CODE] Partition DuckDB backup into < 50MB Parquet segments for GitHub storage.
- [ALL] Target: Deployment to master by noon 2026-02-18.
