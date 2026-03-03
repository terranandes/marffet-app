# Code Review — 2026-03-03 Sync v3
**Reviewer:** [CV]
**Date:** 2026-03-03 22:28 HKT

---

## Scope

Uncommitted tier differentiation changes — 4 files, 126 insertions, 53 deletions.

## Verdict: 🔴 FAIL — 2 Critical Bugs

### Files Reviewed

| File | Change | Risk | Verdict |
|------|--------|------|---------|
| `app/auth.py` | Extract `get_user_tier_by_email()`, refactor `/me` | **CRITICAL** | 🔴 FAIL — Duplicate route + misplaced function |
| `app/config.py` | Add VIP/GM limits (20/100/500 & 30/200/1000 & 1000/1000/10000) | Low | ✅ Values match approved tier matrix |
| `app/services/portfolio_service.py` | 4-tier limit enforcement for create_group, add_target, add_transaction | **CRITICAL** | 🔴 FAIL — Missing 2 import lines |
| `docs/product/specification.md` | Differentiate PREMIUM vs VIP in tier table | Low | ✅ Consistent with config.py values |

---

### BUG-A: `auth.py` — Structural Corruption (CRITICAL)

**Root Cause:** The edit was applied as a patch on top of the old code, but the old `get_me` function body (lines 296-313) was not fully removed.

**Current state (lines 295-396):**
```
L295: @router.get("/me")              ← OLD route (1st registration)
L296: async def get_me(request):
L297-312: ... fetches db_profile ...
L313:     # Check for injected VIP/Premium membership
L314: def get_user_tier_by_email(...): ← WRONG: defined INSIDE old get_me's `with` block
L315-356: ... helper body ...
L357: 
L358: 
L359: @router.get("/me")              ← NEW route (2nd registration)
L360: async def get_me(request):
L361-396: ... uses get_user_tier_by_email ...
```

**Problems:**
1. `get_user_tier_by_email` is a **nested function** (inside old `get_me`) — cannot be imported by other modules.
2. **Duplicate route** `@router.get("/me")` — FastAPI registers both, uses last one.
3. Old `get_me` (L296-313) is **dead code** that runs on import but does nothing useful.

**Fix Required:**
1. Delete lines 295-313 (old `get_me` stub)
2. Dedent `get_user_tier_by_email` to module level (remove 4 spaces from lines 314-356)
3. Ensure only ONE `@router.get("/me")` exists

---

### BUG-B: `portfolio_service.py` — Missing Imports (CRITICAL)

**Root Cause:** The edit replaced the import block (lines 5-7) but dropped two lines:

```diff
  from app.config import (
      FREE_MAX_GROUPS, PREMIUM_MAX_GROUPS, VIP_MAX_GROUPS, GM_MAX_GROUPS,
      ...
  )
+ # MISSING:
+ from app.repositories import user_repo, group_repo, target_repo, transaction_repo
+ from app.services import market_data_service, calculation_service
```

**Impact:** `group_repo`, `target_repo`, `transaction_repo`, `market_data_service`, `calculation_service`, and `user_repo` are used 31+ times throughout the file. Every function call will raise `NameError`.

**Fix Required:** Restore the two import lines after the `config` import block (after line 10).

---

### Verified Correct

| Check | Result |
|-------|--------|
| `config.py` limits | ✅ FREE(11/50/100) → PREMIUM(20/100/500) → VIP(30/200/1000) → GM(1000/1000/10000) |
| `specification.md` tier matrix | ✅ Matches config.py values exactly |
| Tier precedence logic | ✅ GM > VIP > PREMIUM > FREE (in `get_user_tier_by_email` logic) |
| `is_premium` derivation | ✅ `tier in ['PREMIUM', 'VIP', 'GM']` — correct |
| `portfolio_service.py` limit pattern | ✅ Consistent `limits = {...}; limit = limits.get(tier, FREE_*)` across all 3 operations |
| Syntax compilation | ✅ All 3 Python files compile (`py_compile`) — bugs are structural, not syntactic |

### Risks & Recommendations

1. **DO NOT commit these changes until both bugs are fixed.** The code will crash on any portfolio operation.
2. **The limit-check pattern in `portfolio_service.py` uses `from app.auth import get_user_tier_by_email` inside functions** — this is acceptable (lazy import to avoid circular imports) but depends on BUG-A being fixed first.
3. **After fixing**, a local smoke test should exercise: create group, add target, add transaction for a FREE user to confirm limit enforcement works.
4. **No frontend changes were made** — the current frontend already gates on `is_premium` and `tier` from `/auth/me`. The backend changes provide the correct values.
