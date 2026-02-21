# Code Review: 2026-02-20 Evening Sync-up

**Date**: 2026-02-20
**Reviewer**: [CV]
**Scope**: Calculator Terminal Logic & Crawler YFinance Rollback

---

## 1. Changes Reviewed
### 1.1 `app/project_tw/calculator.py`
**Purpose**: Fixing terminal mathematical discrepancies for bankrupt and delisted stocks (e.g., 1606 Kolin).
**Assessment**: ✅ APPROVED. [CODE] introduced logic to check if `sorted_years[-1] < target_max_year`. The loop persists investments mathematically as "frozen" capital alongside a terminal value of 0.0, dragging the simulation to the endpoint. This authentically recreates the -100% / partial salvage decay required by MoneyCome metrics.

### 1.2 `app/project_tw/crawler_tpex.py`
**Purpose**: Resolving BUG-116 by preventing the native TPEx endpoint from returning 2026 ranges for 2006 queries.
**Assessment**: ✅ APPROVED. [CODE] completely shifted historical limit queries (`fetch_one_year`) to use `yf.Tickers` with `auto_adjust=False`, effectively fetching pure nominal prices through YFinance boundaries instead of TPEx. This prevents modern-day data overlaps.

## 2. Open Issues
- `scripts/ops/` is heavily polluted with ad-hoc Python execution frameworks. This must be tidied into `tests/debug_tools/` or a central launcher before pushing.

---
**Signed**: [CV] Code Verification Agent
