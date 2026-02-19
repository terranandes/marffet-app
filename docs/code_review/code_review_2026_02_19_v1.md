# Code Review: Phase 17-A Grand Correlation (2026-02-19 v1)

**Date**: 2026-02-19 00:46 HKT
**Reviewer**: [CV]
**Scope**: Phase 17-A commits — `権息` parser fix, KY/DR normalization, correlation runner

---

## 1. Commits Reviewed

| Commit | Description | Verdict |
|--------|-------------|---------|
| `d1acf05` | feat(phase17a): dividend data accuracy - 権息 fix + KY/DR normalization | ✅ APPROVED |
| `dc19982` | fix(critical): restore pd.notna() calls corrupted by edit tool side-effect | ✅ APPROVED |
| `86d44cf` | fix: correct indentation and pd.isna regression in market_data_service | ✅ APPROVED |
| `673c5a6` | chore: phase 16/17 transition housekeeping | ✅ APPROVED |
| `54f1059` | chore: commit remaining Phase 17-A artifacts and debug scripts | ✅ APPROVED |

---

## 2. Key Changes Reviewed

### 2.1 `crawler.py` — TWT49U `権息` Combined Parser Fix

**Change**: Added `combined` flag detection for `権息` (combined cash+stock) dividend entries.

**Verdict**: ✅ APPROVED
- Correctly identifies combined entries that were previously zeroed out
- Goodinfo patches applied for 426 stocks as fallback
- Match rate improved from 62.9% → 70.8% (±1.5%) — major impact

### 2.2 `scripts/ops/generate_ky_patches.py` (NEW)

**Change**: New script that fetches verified dividend history from `yfinance` for 90+ KY/DR stocks.

**Verdict**: ✅ APPROVED with note
- Correctly identifies KY/DR stocks by suffix pattern
- Fetches per-year cash/stock breakdown from yfinance
- Outputs `data/ref/ky_dividend_patch.json`

**⚠️ Issue**: Large split ratios (e.g., `4763` split 10.0 → stock=90.0) are not capped. This can over-adjust CAGR for stocks with par-value changes. **Recommend**: Add `stock_div = min(stock_div, 20.0)` guard.

### 2.3 `reimport_twse_dividends.py` — KY Integration

**Change**: Added KY patch as highest-priority override (TWT49U → Goodinfo → KY/YFinance).

**Verdict**: ✅ APPROVED
- Priority chain is correct
- 650 KY records patched
- `4763` fixed: 152.46 TWD → 2.5 TWD ✅

### 2.4 `market_data_service.py` — pd.notna() Restoration

**Change**: Restored `pd.notna()` calls that were corrupted by an edit tool side-effect.

**Verdict**: ✅ APPROVED (Critical Fix)
- `pd.isna()` was incorrectly substituted for `pd.notna()` in several places
- This would have caused valid data to be silently skipped
- Regression was caught and fixed in same session

---

## 3. Open Code Quality Items (Carried Forward)

| Issue | File | Severity | Status |
|-------|------|----------|--------|
| Redundant `SAVE_INTERVAL` at L755 | `market_data_service.py` | Low | Open — Phase 17-E |
| Debug prints (`[DEBUG]`) | `market_data_service.py` | Low | Open — Phase 17-E |
| Bare `except` (L909, L919) | `market_data_service.py` | Medium | Open — Phase 17-E |
| Large split ratio cap (≤20.0) | `generate_ky_patches.py` | Medium | **New — Phase 17-A** |

---

## 4. New Bug Filed

### BUG-114-CV: Mobile Portfolio Card Click Timeout

**Severity**: 🟡 Medium (E2E test infrastructure issue)
**Status**: Open / Phase 8

**Root Cause**: Playwright E2E test targets `get_by_text("TSMC", exact=True).first` which resolves to the hidden desktop table row `<div class="font-bold text-white">TSMC</div>` rather than the visible mobile card element.

**Fix Recommendation**:
1. Add `data-testid="mobile-stock-card"` to the mobile card component
2. Use `scroll_into_view_if_needed()` before clicking
3. Or filter by visibility: `get_by_text("TSMC").filter(visible=True).first`

**Related**: BUG-113-CV (same root cause)

---

## 5. Grand Correlation Results Summary

| Run | Match (±1.5%) | Match (±3.0%) | MAE | Key Change |
|-----|:---:|:---:|:---:|---|
| v4 (baseline) | 62.9% | 78.8% | 2.17% | CAGR year alignment |
| v5 (Phase 1) | 70.8% | 82.2% | ~1.9% | TWT49U `権息` parser + Goodinfo |
| v6 (Phase 2) | 71.2% | 82.1% | ~1.9% | KY/DR YFinance normalization |
| **v7 (projected)** | **~72%** | **~83%** | **~1.8%** | Large split cap fix |

**Remaining Gap Analysis**:
- ~2%: Missing OTC history (TPEx→TWSE transferred stocks)
- ~1%: Large split ratio distortion (fixable with cap)
- ~0.5%: Genuine outliers (mergers, reverse splits)

---

## 6. Risk Assessment

- **Data Safety**: All changes are additive. `ON CONFLICT DO UPDATE` ensures idempotency.
- **Rollback**: DuckDB can be rebuilt from MI_INDEX Parquet snapshots if needed.
- **Production Risk**: Low. Changes are data import scripts, not live API handlers.

---

**Signed**: [CV] Code Verification Agent
**Next Review**: After Phase 17-A v7 (large split cap fix) + Phase 17-B/C deployment.
