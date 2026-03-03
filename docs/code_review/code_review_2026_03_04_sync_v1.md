# Code Review — 2026-03-04 Sync v1
**Reviewer:** [CV]
**Date:** 2026-03-04 03:15 HKT

---

## Files Changed (This Session)

### 1. `frontend/src/app/compound/page.tsx` — PASS ✅

**Commits:** `fd33f1c`, `a0aeb4d`

| Aspect | Verdict | Notes |
|--------|---------|-------|
| Logic | ✅ | Unified X-axis from `Set` of all stocks' years, `Map` lookup with null padding |
| Edge Cases | ✅ | `connectNulls: false` prevents lines through null gaps |
| Color | ✅ | Stock 3 changed to gold `#FFD700` (better contrast vs cyan/red) |
| Performance | ✅ | `Set` + `Map` lookups are O(n), no perf concern |
| i18n | ✅ | No hardcoded strings |

### 2. `app/services/roi_calculator.py` — PASS ✅ (with note)

**Commits:** `b701741`, `e4d0448`

| Aspect | Verdict | Notes |
|--------|---------|-------|
| Logic | ✅ | Gap detection: years < 20 days excluded, contiguous groups split, latest group kept |
| Edge Cases | ⚠️ | Continuous 興櫃→IPO transition (no gap) will still include 興櫃 data. Documented as known limitation. |
| Performance | ✅ | Single pass groupby + linear scan, negligible overhead |
| Scope | ✅ | Only affects the slow-path (per-stock calculation), not the fast precomputed path |

**Note:** The gap detection filter is applied at line 207-224 in the `else` branch (non-precomputed path). The `precomputed_yearly_stats` path at line 185 does NOT have this filter — acceptable since bulk MarsStrategy uses its own year filtering.

### 3. `docs/jira/BUG-012-CV_home_i18n_keys_raw.md` — PASS ✅

Properly formatted JIRA ticket with reproduction steps, evidence screenshot, and fix recommendation.

---

## Summary

**Verdict: ✅ PASS — All changes correctly scoped and functional.**

- 3 files changed across 4 commits
- `+36 / -5` lines
- No regressions detected
- 1 known limitation documented (continuous 興櫃→IPO edge case)

---

## Recommendations

1. Consider applying the same gap filter to the `precomputed_yearly_stats` path for consistency (currently only affects detail API, not bulk Mars Strategy)
2. The `portfolio.db` auto-backup commits are cluttering `git log` — consider `.gitignore` or weekly-only commits
