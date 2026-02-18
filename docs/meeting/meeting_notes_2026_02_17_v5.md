# Meeting Notes: Data Integrity & General Sync
**Date**: 2026-02-17 18:20 HKT
**Version**: v5
**Topic**: Data Integrity Backfill Status & General Triage

## 1. Project Status
- **[PL] Overview**: 
  - The "Data Integrity Siege" (2000-2004 Backfill) is currently running via the new **Resumable Script** (`scripts/ops/backfill_2000_2004_resumable.py`).
  - Progress: ~32% (Batch ~680/2100).
  - Stability: Excellent. `chunk_size=1` fixed the `yfinance` 1.0 hang/crash issues.
  - Recovery: Fully resumable.

- **[CODE] Technical Implementation**:
  - `market_data_service.py` is now robust.
  - `load_stock_list` helper restored.
  - `supplement_splits.py` created to auto-patch "Implied Split" vs "Recorded Split" discrepancies.

## 2. Issues & Triage
- **Jira Review**:
  - `BUG-112-PL_mars_data_discrepancy`: This is the root cause of the current backfill. Will be marked [RESOLVED] once verification passes.
  - `BUG-111-CV_nextjs_api_proxy_500`: Still open (Next.js proxy issue). Lower priority while we fix data.
  - `BUG-10x` series (Mobile/E2E): Pending frontend cycle.

## 3. Road Ahead (Next 24h)
1. **Finish Backfill**: ETA 19:30 HKT.
2. **Verification**: Run `verify_splits_2000_2004.py`.
3. **Supplementation**: Run `supplement_splits.py --apply`.
4. **Simulation**: Run "Mars Strategy Simulation" (Full 24 years) to validate the clean data.
5. **Deployment**: Push clean DB (or update script) to Zeabur.

## 4. Documentation
- `docs/code_review/code_review_2026_02_17.md`: Approved.
- `docs/product/mars_strategy_bcr.md`: Needs update after Simulation confirms 2000-2004 data is valid.

## 5. Decisions
- **Decision 1**: Maintain `chunk_size=1` for all future bulk backfills to ensure stability.
- **Decision 2**: Use `supplement_splits.py` as the standard tool for fixing "Implied vs Recorded" split data.

**Reported by**: [PL] Terran's Assistant
