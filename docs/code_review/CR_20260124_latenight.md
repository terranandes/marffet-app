# Code Review: Session 2026-01-24 Late Night

**Reviewer**: [CV]  
**Date**: 2026-01-24  
**Focus**: Critical fixes from today's session

---

## 1. Critical Fix: `get_target_summary` Column Mismatch

**File**: `app/portfolio_db.py` (Lines 670-682)  
**Commit**: `eecfe68`

### Issue
```python
# BEFORE (Broken)
SELECT ex_date, shares_held, unit_cash, total_cash
# Schema had: amount_per_share, NOT unit_cash
```

### Fix
```python
# AFTER (Fixed)
SELECT ex_date, shares_held, amount_per_share, total_cash
```

**Root Cause Analysis**:
- This was a **latent bug** present since early development.
- It only triggered when `dividend_history` table had records.
- Bug existed at `d9c3426` (stable base) but was dormant.

**Recommendation**: 
- Add schema validation test to catch column mismatches at startup.
- Consider using ORM (SQLAlchemy) for type-safe queries.

---

## 2. Taiwan Color Convention

**Files**: 
- `app/static/main.js` (Lines 1378-1386)
- `frontend/src/app/portfolio/page.tsx` (Line 721)

**Change**: Swapped BUY/SELL colors for Taiwan convention.

| Type | Before | After |
|------|--------|-------|
| BUY | Green | **Red** |
| SELL | Red | **Green** |

**Status**: ✅ Correct implementation, matches Taiwan stock market convention.

---

## 3. BCR Premium Gating

**File**: `frontend/src/app/race/page.tsx`  
**Commit**: `1d1ce9d`

### Implementation
```tsx
const isPremium = user?.is_admin || (user?.subscription_tier && user.subscription_tier > 0);

// CAGR button shows lock icon for non-premium
{!isPremium && <span className="text-xs">🔒</span>}
```

**Security Check**: ✅ Properly checks `is_admin` OR `subscription_tier > 0`.

**Recommendation**: Backend should also enforce this check to prevent API abuse.

---

## 4. Build Error Fix

**File**: `frontend/src/app/viz/page.tsx`  
**Commit**: `73c245f`

**Issue**: Missing `data` and `loading` state variables after user state was added.

**Fix**: Added missing state declarations.

**Lesson**: When adding new state, always verify existing state variables are preserved.

---

## Summary

| Item | Severity | Status |
|------|----------|--------|
| Column mismatch | 🔴 Critical | ✅ Fixed |
| Color convention | 🟡 Medium | ✅ Fixed |
| Premium gating | 🟢 Feature | ✅ Implemented |
| Build error | 🔴 Critical | ✅ Fixed |

**Overall Assessment**: Session successfully addressed all critical issues. Code quality maintained.
