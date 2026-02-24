# Code Review Note (Mars Unification & Cleanup)
**Date:** 2026-02-25 03:10 HKT
**Reviewer:** [CV]

## 1. Changes Since Last Review

### Backend (app/main.py & app/services/strategy_service.py)
- **DuckDB ORDER BY**: Added `ORDER BY stock_id, date ASC` to `MarsStrategy.analyze` block. Ensures pandas aggregation operations (`groupby().first()`) output purely deterministic mathematical results, preventing data racing.
- **API detail Unification**: Refactored `/api/results/detail` to import `app.services.roi_calculator.ROICalculator` instead of the legacy `app.project_tw` calculator. 
- **Dividend Patching**: Added `json.load()` pipeline for `data/dividend_patches.json` inside the detail API. Missing historical dividend overlays (e.g. 2330 in 2006) are now properly applied to the visual chart array.

### Workflows (.agent/workflows/)
- Boss pushed updates to `clean-br-wt.toml` and `agents-sync-meeting.toml` to mandate git stash inclusion during housekeeping sweeps.

## 2. Remote Deployment Check
- Not deployed yet. Local environments validated the fix: Both summary API and detail chart API independently compute a TSMC 2006 final value of `90,629,825.0`, eliminating the ~900 NTD difference.

## 3. Verdict
- **Production Code:** APPROVED. The fix is mathematically sound, deletes technical debt, and enforces a single source of truth for CAGR.
- **Housekeeping:** APPROVED. 11 remote repositories and 2 stashes purged.
- **Next Step:** Commit docs and proceed to E2E isolated worktree verification.
