# Meeting Notes: Agents Sync-Up
**Date**: 2026-02-06
**Version**: v1
**Participants**: [PM], [PL], [SPEC], [CODE], [UI], [CV]

---

## 1. Project Progress

**[PM] Product Manager**:
- **Mars Strategy Engine Revamp (Phase 1)**: Core migration of the Main Table (`/api/results`) to the Precision Engine (`ROICalculator`) has been completed. This aligns all wealth calculations (Chart, Modal, Race, Table) to a single source of truth.
- **Compound Interest Tab**: Deployed and stable.
- **User Feedback**: No new critical user feedback since last sync.

**[PL] Project Leader**:
- **Velocity**: Strong progress on Phase 1. The key backend refactor (`run_mars_simulation` → `ROICalculator`) was completed today.
- **Uncommitted Changes**: `app/main.py`, `app/project_tw/calculator.py` are modified. A new verification script `tests/verify_precision_migration.py` was created.
- **Worktree**: Clean. Single `master` branch.

---

## 2. Current Bugs (Jira Triage)

**[CV] Code Verifier**:
| Ticket | Status | Notes |
|--------|--------|-------|
| BUG-001 | Closed/Low Priority | E2E Add Stock Timeout (Flaky Network) |
| BUG-005 | Closed | Settings Selector (Fixed) |
| BUG-006 | Monitor | Test Env Flakiness (Non-Blocking) |
| BUG-007 | Closed | Transaction Modal Timeout (Fixed) |
| BUG-008 | Closed | Mobile Login Overlay (Fixed) |
| BUG-009 | Monitor | Mobile Google Login (Deferred to OAuth scope expansion) |
| BUG-010 | Closed | Zeabur Guest Mode Login (Fixed via self-heal schema) |
| BUG-011 | **Open** | Transaction Edit Broken (Requires Investigation) |
| BUG-101-104 | Closed/Monitor | [CV]-Reported E2E Flakiness |

**Triage Decision**: BUG-011 (Transaction Edit) is now the **highest priority bug** for next sprint.

---

## 3. Performance Improvement

**[CODE] Backend Dev**:
- **Precision Engine Performance**: Measured `run_mars_simulation` (1700 stocks) at approximately **1.5-2 seconds** after initial `MarketCache` load. Acceptable.
- **`MarketCache` Lazy Loading**: Successfully implemented. Zeabur no longer times out on startup.

**[SPEC] Architect**:
- **Data Granularity**: The new system correctly prioritizes Daily data (Schema V2) if available, falling back to Yearly summary (V1). This is crucial for accurate CAGR.

---

## 4. Features Implemented (This Sync Period)

1.  ✅ **Mars Modal: Triple Curve Chart** (BAO, BAH, BAL) using `detailResult` data.
2.  ✅ **Main Table Migration** to `ROICalculator`.
3.  ✅ **JSON Serialization Fix** for Numpy types (`sanitize_for_json`).
4.  ✅ **ROICalculator Enhancement**: Added `invested`, `roi`, `cagr` to history output.

---

## 5. Features Unimplemented / Deferred

**[PM] Product Manager**:
- **Splits/CapReduction Handling**: Deferred. `handle_corporate_actions` not yet implemented.
- **`unadjusted_prices` toggle in UI**: Deferred.
- **Phase 2 Data Lake (Parquet/DuckDB)**: Not started.

---

## 6. Features Planned (Next Phase)

- **Phase 2**: Universal Data Lake with Parquet/DuckDB storage.
- **Phase 3**: Correlation verification script (`correlate_mars.py`).

---

## 7. Deployment Completeness

**[PL] Project Leader**:
- **Zeabur Status**: Last known deployment is stable.
- **Pending Push**: The Precision Engine changes are **NOT YET pushed** to `origin/master`. Local E2E verification is pending.
- **Action Items**:
    1. Commit `app/main.py`, `app/project_tw/calculator.py`, `tests/verify_precision_migration.py`.
    2. Push to `origin/master`.
    3. Run remote E2E check.

---

## 8. Local vs. Zeabur Discrepancies

**[CV] Code Verifier**:
- **Known Issue**: `MarketCache.get_prices_db(force_reload=True)` was causing startup timeouts on Zeabur. **Resolved** with lazy loading.
- **Current Discrepancy**: None known after the migration.

---

## 9. Code Review Summary

**[CV] Code Verifier**:
- Reviewed `app/main.py` (`run_mars_simulation` refactor).
- **Observation**: The old legacy logic (lines 830-885) has been cleanly replaced. No dead code remains.
- **Concern 1**: The `prices_db` and `dividends_db` arguments are passed to `run_mars_simulation` but **no longer used** (data is fetched via `MarketCache`). Consider removing these arguments for cleaner API design.
- **Concern 2**: The function still has an `import pandas` inside the function body. While functional, top-level imports are preferred for consistency.
- **Verdict**: Code is functional. Minor cleanup recommended post-release.

---

## 10. Mobile Web Layout

**[UI] Frontend Dev**:
- **Status**: No new mobile regressions reported. The Mars page renders correctly on narrow viewports.
- **Todo**: Review the new Triple-Curve chart tooltip on mobile for tap accessibility.

---

## 11. Summary & Next Steps

**[PL] Project Leader**:

| Item | Owner | Priority |
|------|-------|----------|
| Commit & Push Precision Engine | [CODE] | P0 |
| Investigate BUG-011 (Transaction Edit) | [CV] | P1 |
| Start Phase 2 Planning | [SPEC] | P2 |
| Clean up `run_mars_simulation` API signature | [CODE] | P3 |

---

**To Run the App Locally:**
```bash
cd /home/terwu01/github/martian
./start_app.sh
```
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

---

**Signed**,
*[PL] Project Leader*
