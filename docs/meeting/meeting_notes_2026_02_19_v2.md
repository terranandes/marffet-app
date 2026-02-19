# Agents Sync-Up Meeting
**Date**: 2026-02-19 14:08 HKT
**Version**: v2
**Attendees**: [PM] [SPEC] [PL] [CODE] [UI] [CV]

---

## 1. Progress Since Last Meeting (v1 — 00:46 HKT Today)

**[PL]**: Since v1 meeting (9+ hours ago), the following work occurred in this session:

| Item | Description | Status |
|------|-------------|--------|
| Mars Strategy Filters | 5 filters restored in `strategy_service.py` | ✅ Done |
| Name Resolution Fix | Fallback to DuckDB `stock_name` in `app/main.py` | ✅ Done |
| Code Cleanup | Removed `SAVE_INTERVAL`, fixed bare `except` | ✅ Done |
| 9958 Data Purge + Reload | Emergency fix for corrupt/bad price data | ✅ Done |
| Unit Test | `test_mars_filters.py` created | ✅ Done |
| Phase 17-B Verification | BOSS testing locally | 🔄 In Progress |

**[CODE]**: 2 commits on `master` ahead of `origin/master`:
- `f439816` — gitignore + ky split cap + correlation v7
- `7917bd0` — revert split cap + correlation v8

---

## 2. Bug Triage — NEW: 9958 Data Discrepancy

**[CV]**: BOSS reported 9958 (世紀鋼) discrepancy during Phase 17-B verification:

| Metric | Ours | MoneyCome | Gap |
|--------|------|-----------|-----|
| BAO Final Value | NT$45,697,458 | NT$19,706,620 | **2.3x** |
| BAO Total ROI | 1977.16% | 820.9% | **2.4x** |
| CAGR | 17.40% | 12.4% | +5.0% |

### Root Cause Analysis

**[SPEC]**: Three independent issues found:

1. **Missing Dividends** (2022, 2023 absent from DuckDB)
   - Our DuckDB had dividends jumping from 2021 → 2024
   - MoneyCome had 2022 (2.989 TWD) and 2023 (0.494 TWD)
   - **Status**: ✅ Fixed — reloaded from YFinance (16 records now)

2. **Bad Price Ticks** (50% drops in 2023)
   - Two rows showed 50% price drops (182→97 on 2023-03-15, 181→110 on 2023-06-06)
   - No actual split occurred (confirmed via web search + YFinance)
   - Our `SplitDetector` may have falsely doubled the share count
   - **Status**: ✅ Fixed — full price history reloaded from YFinance (4,399 rows)

3. **⚠️ Adjusted vs Nominal Dividends** (Systemic Issue)
   - YFinance `actions` returns **split-adjusted dividends** (deflated by historical splits)
   - Our system uses **nominal (unadjusted) prices** from MI_INDEX
   - Combining nominal prices + adjusted dividends creates inconsistency
   - Affects ALL stocks with historical splits (esp. KY/DR stocks using YFinance patches)
   - **Status**: 🔴 **OPEN** — needs investigation across entire universe

### Name Display Bug

**[UI]**: BOSS also reported many stocks showing ID instead of Chinese name.

**Root Cause**: `app/main.py` uses `stock_list_s2006e2026_filtered.xlsx` for name lookup. Stocks not in this Excel (e.g., 9958) fall back to ID.

**Fix Applied**: `app/main.py` now uses `res.get('stock_name', sid)` as fallback, which reads from DuckDB `stocks` table.

---

## 3. Current Git Status

**[CODE]**: `master` is 2 commits ahead of `origin/master`.

### Uncommitted Changes (Working Tree)

| Category | Files | Action |
|----------|-------|--------|
| **Modified Source** | `app/main.py` (name fix), `strategy_service.py` (filters), `market_data_service.py` (cleanup) | 🔴 Commit |
| **New Test** | `tests/unit/test_mars_filters.py` | 🔴 Commit |
| **New Debug** | `tests/debug_tools/inspect_9958.py`, `reload_9958.py` | 🔵 Commit |
| **New Ops** | `scripts/ops/purge_stock.py` | 🔵 Commit |
| **Docs** | `mars_strategy_bcr.md` (filter docs), `tasks.md` (progress) | 🔴 Commit |
| **Jira** | `BUG-114-CV` | 🔴 Commit |
| **Meeting/Review** | `meeting_notes_2026_02_19_v1.md`, `code_review_2026_02_19_v1.md` | 🔴 Commit |
| **Stale Debug** | `goodinfo_curl.html`, `mops_curl.html`, `mops_debug.html` | 🗑️ Delete |
| **Data** | `data/raw_dividends/*.json`, `data/ref/ky_dividend_patch.json` | Already gitignored |

---

## 4. Performance

**[CODE]**: No regressions. Baseline unchanged:
- **Mars Full Universe**: ~12s (1,604 stocks)
- **Mars with Filters**: Faster frontend load (fewer results to render)

---

## 5. Features Implemented (This Session)

| Feature | Owner | Notes |
|---------|-------|-------|
| Mars Strategy 5 Filters | [CODE] | Active, Duration, Volatility, Stability, ETF |
| Name Resolution Fallback | [CODE] | DuckDB `stocks` table as backup |
| `SAVE_INTERVAL` removal | [CODE] | Simplified chunk-based DuckDB flushes |
| Bare `except` fixes | [CODE] | L154, L361 in `market_data_service.py` |
| 9958 Emergency Data Fix | [CODE] | Purge + reload via individual YFinance fetch |

---

## 6. Features Unimplemented / Deferred

| Feature | Phase | Blocker |
|---------|-------|---------|
| YFinance Adjusted Dividend Correction | 17-A+ | 🔴 Systemic — affects all split stocks |
| Parquet Backup | 17-D | Not started |
| Zeabur Volume Persistence | 17-C | Infrastructure config |
| Mobile Premium Overhaul | 8 | Pending Phase 8 |

---

## 7. Phase 17 Status

| Part | Status | Details |
|------|--------|---------|
| **E — Housekeeping** | ✅ Completed | Filters, cleanup, bare except fixes |
| **A — Grand Correlation** | 🟡 v8: **71.20% / 82.09%** | Adjusted dividend issue may affect accuracy |
| **B — Local Verification** | 🟡 **In Progress** | BOSS found 9958 discrepancy, investigating |
| **C — Zeabur Deployment** | ⬜ Not Started | Blocked on 17-B/D |
| **D — Nightly Pipeline** | ⬜ Not Started | Blocked on 17-C |

---

## 8. Worktree / Branch Status

| Branch | Status | Action |
|--------|--------|--------|
| `master` | 2 commits ahead of origin | 🔴 Push after commit |
| `ralph-loop-q05if` | Local, stale | 🗑️ Clean up |
| 8 remote `ralph-loop-*` branches | Stale | 🗑️ Clean up |
| `feat/settings-modal-migration` | Remote, merged | 🗑️ Clean up |
| `test/full-exec` | Remote | 🗑️ Clean up |

---

## 9. New Jira Ticket

### BUG-115-PL: YFinance Adjusted Dividend Data Mismatch

**Severity**: 🔴 High (Data Accuracy)
**Status**: Open
**Owner**: [CODE]

YFinance `actions` API returns split-adjusted dividends. Our system uses nominal prices from MI_INDEX. The combination overstates wealth for stocks with historical splits. Affects ~200+ stocks with splits in the 2000-2025 range.

**Fix Options**:
1. Multiply YFinance dividends by cumulative split ratio to "un-adjust" them
2. Use TWSE/Goodinfo as primary dividend source (already done for most stocks — only KY/DR use YFinance)
3. Cross-validate all dividend sources against TWSE official records

---

## 10. Decisions & Action Items

| # | Decision / Action | Owner | Priority | Deadline |
|---|-------------------|-------|----------|----------|
| 1 | **Commit all working tree changes** (filters, name fix, cleanup) | [CODE] | 🔴 High | This session |
| 2 | **File BUG-115** (YFinance adjusted dividends) | [PL] | 🔴 High | This session |
| 3 | **Investigate adjusted dividend impact** on Grand Correlation | [CODE] | 🟡 Medium | Next session |
| 4 | **Clean up stale branches** (9 remote + 1 local) | [CODE] | 🟡 Medium | This week |
| 5 | **Delete debug HTML files** (goodinfo, mops) | [CODE] | 🔵 Low | This session |
| 6 | **Continue Phase 17-B verification** with BOSS | BOSS | 🟡 | Ongoing |
| 7 | **Push to origin/master** after commit | [CODE] | 🔴 High | After commit |

---

## [PL] Summary Report to Terran

Boss, here's where we stand at 14:08 HKT (2026-02-19):

### What We Did
1. **Mars Strategy Filters** — 5 quality filters restored and working (Active, Duration >3yr, Volatility <3x TSMC, Stability Std<20, No Leveraged ETFs)
2. **Name Display Fix** — Stocks now show Chinese names from DuckDB instead of raw IDs
3. **9958 Emergency Fix** — Purged corrupt data, reloaded 4,399 prices + 16 dividends from YFinance

### What We Found
🔴 **9958 Discrepancy** — Our final value (NT$45M) is 2.3x higher than MoneyCome's (NT$19M). Root causes:
- Missing 2022/2023 dividends (fixed)
- Bad price ticks causing false split detection (fixed)
- **YFinance adjusted dividends vs nominal prices** (systemic — filed as BUG-115)

### What's Next
1. Commit all changes + push to origin
2. Investigate adjusted dividend impact across universe
3. Continue Phase 17-B verification
4. Phase 17-C Zeabur deployment after verification

---

**Reported by**: [PL]
**Next Meeting**: After Phase 17-B completion or BUG-115 resolution.
