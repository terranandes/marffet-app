# Code Review: Evening Session
**Date**: 2026-02-06 21:33
**Reviewer**: [CV] Code Verifier
**Scope**: Today's hotfixes and Split Detector integration

---

## 1. Files Reviewed

| File | Change Summary | Verdict |
|------|---------------|---------|
| `app/main.py` | Fixed `contribution` → `annual_investment=contribution` | ✅ APPROVED |
| `app/project_tw/calculator.py` | Added pre-detection call `detector.detect_splits()` | ✅ APPROVED |
| `scripts/verify_universal.py` | Changed `FIRST_OPEN` → `FIRST_CLOSE` | ✅ APPROVED |

---

## 2. Critical Findings

### Issue 1: Argument Name Mismatch (RESOLVED)
**Location**: `app/main.py` line 868
**Problem**: Positional argument `contribution` didn't match `annual_investment` keyword.
**Impact**: 500 Internal Server Error on `/api/results`.
**Resolution**: Changed to `annual_investment=contribution`.

### Issue 2: Split Detection Not Triggered (RESOLVED)
**Location**: `app/project_tw/calculator.py` `calculate_complex_simulation()`
**Problem**: `detect_splits()` was never called before `get_cumulative_ratio()`.
**Impact**: 0050 showed 5% CAGR instead of 12.1%.
**Resolution**: Added pre-detection call at line 167-170.

---

## 3. Recommendations

1. **Add Unit Tests**: `test_split_detector.py` to prevent regression.
2. **Document MoneyCome Rules**: Add comments in `calculator.py` explaining:
   - `FIRST_CLOSE` = First trading day closing price.
   - Dividend reinvestment at annual average price.
3. **Cleanup Debug Scripts**: Move `analyze_split_impact.py`, `investigate_buy_logic.py` to `scripts/debug/` after verification.

---

## 4. Approval

**[CV]**: All changes are correct and safe to deploy. Recommend **immediate commit and push**.

---

**Signed**,
*[CV] Code Verifier*
