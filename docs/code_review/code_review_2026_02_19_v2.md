# Code Review: Mars Filters + Name Fix + 9958 Data Repair (2026-02-19 v2)

**Date**: 2026-02-19 14:08 HKT
**Reviewer**: [CV]
**Scope**: Uncommitted changes in working tree — Mars filters, name resolution, code cleanup, 9958 data fix

---

## 1. Changes Reviewed

### 1.1 `app/main.py` — Name Resolution Fix

```diff
-res['name'] = name_map.get(sid, sid)
+res['name'] = name_map.get(sid, res.get('stock_name', sid))
```

**Verdict**: ✅ APPROVED
- Falls back to DuckDB `stock_name` (from `MarsStrategy.analyze`) when Excel lookup fails
- Zero risk — additive change, preserves existing behavior for stocks in Excel
- Fixes BOSS-reported issue of stocks showing raw IDs

### 1.2 `app/services/strategy_service.py` — Mars Filters

**Changes**:
- Added `end_year` to result metrics (for Active filter)
- Added `apply_filters()` method with 5 sequential filters
- Called `apply_filters()` at end of `analyze()`

**Verdict**: ✅ APPROVED
- Filter order is logical (cheapest checks first)
- TSMC baseline is correctly identified with `next()` fallback
- Rejection counting provides good observability
- `cagr_std > 20` default of 999.0 ensures stocks without enough data are filtered

### 1.3 `app/services/market_data_service.py` — Code Cleanup

**Changes**:
- Removed `SAVE_INTERVAL` logic (L829-833)
- Simplified to flush at end of each chunk
- Fixed bare `except:` → `except Exception:` (L154, L361)

**Verdict**: ✅ APPROVED
- `SAVE_INTERVAL` was redundant with chunk-based processing
- DuckDB handles transaction batching internally
- `except Exception` is proper Python practice

### 1.4 `tests/unit/test_mars_filters.py` — New Unit Test

**Verdict**: ✅ APPROVED
- Tests all 5 filter conditions with mock data
- Includes TSMC baseline for volatility comparison
- Clean AAA pattern

### 1.5 `tests/debug_tools/inspect_9958.py`, `reload_9958.py` — Debug Scripts

**Verdict**: ✅ APPROVED (debug tools)
- `inspect_9958.py`: Diagnostic for DuckDB data verification
- `reload_9958.py`: Emergency reload using individual yfinance fetch
- Both correctly placed in `tests/debug_tools/`

### 1.6 `scripts/ops/purge_stock.py` — New Ops Script

**Verdict**: ✅ APPROVED
- Clean utility for deleting stock data from DuckDB
- Properly uses `get_connection()` helper
- CLI interface with argument validation

---

## 2. Open Issues

| Issue | File | Severity | Status |
|-------|------|----------|--------|
| YFinance adjusted dividends | All KY/DR stocks | 🔴 High | **NEW — BUG-115** |
| Large split ratio cap | `generate_ky_patches.py` | 🟡 Medium | Reverted in v8 |
| Debug prints | `market_data_service.py` | 🔵 Low | Carried forward |

---

## 3. Risk Assessment

- **Data Safety**: 9958 was purged and reloaded. Other stocks unaffected.
- **Filter Impact**: Some previously-shown stocks may now be filtered out. This is intentional per BOSS's request.
- **Adjusted Dividend Issue**: BUG-115 is systemic but only affects KY/DR stocks (~90 stocks). The majority of the universe uses TWSE official dividends which are already nominal.

---

**Signed**: [CV] Code Verification Agent
**Next Review**: After BUG-115 investigation + commit/push.
