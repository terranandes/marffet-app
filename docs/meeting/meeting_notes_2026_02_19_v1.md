# Agents Sync-Up Meeting
**Date**: 2026-02-19 00:46 HKT
**Version**: v1
**Attendees**: [PM] [SPEC] [PL] [CODE] [UI] [CV]

---

## 1. Progress Since Last Meeting (2026-02-18 v6)

**[PL]**: New session. Since v6 (23:50 HKT yesterday), the following commits have landed on `origin/master`:

| Commit | Description |
|--------|-------------|
| `54f1059` | chore: commit remaining Phase 17-A artifacts and debug scripts |
| `d1acf05` | feat(phase17a): dividend data accuracy - 権息 fix + KY/DR normalization |
| `dc19982` | fix(critical): restore pd.notna() calls corrupted by edit tool side-effect |
| `86d44cf` | fix: correct indentation and pd.isna regression in market_data_service |
| `673c5a6` | chore: phase 16/17 transition housekeeping |

**[CODE]**: `master` is now synced with `origin/master`. Phase 17-A (Grand Correlation) changes are committed and pushed.

---

## 2. Current Git Status

**[CODE]**: Working tree has untracked/modified files:

| Category | Files | Action |
|----------|-------|--------|
| Modified data | `data/raw_dividends/TWSE_Dividends_201*.json` (16 files) | ⚠️ Add to `.gitignore` |
| Modified test evidence | `tests/evidence/*.png` (3 files) | 🔵 Commit or ignore |
| New debug scripts | `scripts/debug_backfill_1101.py`, `scripts/verify_backfill.py` | 🔵 Move to `tests/ops_scripts/` |
| New Jira ticket | `docs/jira/BUG-114-CV_mobile_portfolio_card_click_timeout.md` | ✅ Commit |
| Analysis CSVs | `tests/analysis/bad_ticks.csv`, `cliff_stocks_2005.csv`, `mismatched_splits_2000_2004.csv` | 🔵 Commit |
| Playwright screenshot | `.playwright-mcp/page-*.png` | 🗑️ Ignore |
| Debug HTML files | `goodinfo_curl.html`, `mops_curl.html`, `mops_debug.html` | 🗑️ Delete |
| Intermediate data | `data/intermediate_candidates_v2.txt` | 🔵 Commit or ignore |

---

## 3. Bug Triage

| Ticket | Severity | Status | Owner | Notes |
|--------|----------|--------|-------|-------|
| TWT49U `權息` Parser | 🔴 Critical | ✅ **RESOLVED** | [CODE] | Phase 17-A Phase 1 — Goodinfo patches for 426 stocks |
| KY/DR Data Corruption | 🔴 Critical | ✅ **RESOLVED** | [CODE] | Phase 17-A Phase 2 — YFinance patches for 90 stocks |
| Large Split Ratio Distortion | 🟡 Medium | **Open** | [CODE] | KY stocks with par-value changes (e.g., 4763 split 10.0 → stock=90.0). Cap needed. |
| BUG-114-CV (Mobile Card Click Timeout) | 🟡 Medium | **New / Open** | [UI] | Playwright E2E: TSMC card found but not visible. Phase 8. |
| BUG-113-CV (Mobile Card Expand) | 🟡 Low | Open | [UI] | CSS z-index / visibility. Phase 8. |
| BUG-112-CV (TX Modal Timeout) | 🟡 Medium | Open | [UI] | E2E timeout. Phase 8. |
| BUG-009 (Mobile Google Login) | 🟡 Medium | Open | [CODE] | Deferred → Phase 8 |
| BUG-010 (Zeabur Guest Mode) | 🟡 Medium | Open | [CODE] | Deferred → Phase 8 |

**[CV]**: BUG-114 is newly filed this session. It is consistent with BUG-113 (same element visibility issue in mobile viewport). Both are Phase 8 items, non-blocking for data work.

---

## 4. Performance

**[CODE]**: No new performance changes. Baseline unchanged:
- **Mars Full Universe**: 1,604 stocks in **12.25s** (131 stocks/sec)
- **Grand Correlation v6**: 71.2% (±1.5%), 82.1% (±3.0%), MAE ~1.9%

---

## 5. Features Implemented (Phase 17-A — Partial)

| Feature | Status | Notes |
|---------|--------|-------|
| TWT49U `權息` combined parser fix | ✅ Done | `crawler.py` — combined flag logic |
| Goodinfo dividend patches (`goodinfo_dividends.json`) | ✅ Done | 426 stocks patched |
| KY/DR normalization (`ky_dividend_patch.json`) | ✅ Done | 90 stocks, 650 records patched |
| `generate_ky_patches.py` | ✅ Done | Fetches yfinance for KY/DR stocks |
| `reimport_twse_dividends.py` KY integration | ✅ Done | Priority: TWT49U → Goodinfo → KY/YFinance |
| `correlate_all_stocks.py` | ✅ Done | Grand Correlation runner |
| `correlation_report_full.csv` | ✅ Done | Saved to `docs/product/` |

---

## 6. Features Unimplemented / Deferred

| Feature | Phase | Blocker |
|---------|-------|---------|
| Grand Correlation >85% match | 17-A | OTC history gap (~2%), large split cap (~1%) |
| OTC crawler (TPEx→TWSE transferred stocks) | Future | New data source needed |
| Large split ratio cap in `generate_ky_patches.py` | 17-A | Not implemented yet |
| Parquet Backup (<50MB) | 17-D | Not started |
| Zeabur Volume Persistence | 17-C | Infrastructure config |
| Direct DB Upload to Zeabur | 17-C | Volume mount needed |
| Mobile Premium Overhaul | 8 | Pending Phase 8 cycle |
| Interactive Backfill Dashboard | 8 | Low priority |

---

## 7. Phase 17 Status

| Part | Status | Details |
|------|--------|---------|
| **E — Housekeeping** | ✅ Completed | Branches cleaned, code quality items addressed |
| **A — Grand Correlation** | 🟡 **71.2% / 82.1%** | Phase 1+2 done. Remaining: OTC gap + split cap |
| **B — Local Verification** | ⬜ Not Started | Pending Boss |
| **C — Zeabur Deployment** | ⬜ Not Started | Blocked on 17-B/D |
| **D — Nightly Pipeline** | ⬜ Not Started | Blocked on 17-C |

---

## 8. Deployment Status

**[CODE]**: `master` is synced with `origin/master` (5 commits pushed since last meeting).

| Aspect | Local | Zeabur | Action Needed |
|--------|-------|--------|---------------|
| `market.duckdb` | ✅ Phase 16+17A clean | ❓ Stale | Volume mount (Phase 17-C) |
| Phase 17-A Fixes | ✅ Applied | ❌ Not deployed | Push done; Zeabur auto-deploy pending |
| Auth / Login | ✅ Working | ❓ Last verified 02-09 | Retest after 17-C |
| Frontend | ✅ Working | ❓ | Retest after 17-C |

---

## 9. Worktree / Branch Status

| Branch | Status | Action |
|--------|--------|--------|
| `master` | ✅ Synced with origin | Active |
| `ralph-loop-q05if` | Latest Ralph Loop test | Keep for reference |
| `ralph-loop-6taxy` | Stale | 🗑️ Clean up |
| `ralph-loop-kxvdg` | Stale | 🗑️ Clean up |
| `ralph-loop-uf966` | Stale | 🗑️ Clean up |
| `ralph-loop-3ox9f` | Local only, stale | 🗑️ Clean up |
| `feat/settings-modal-migration` | Remote only, merged | 🗑️ Clean up |
| `test/full-exec` | Remote only | 🗑️ Clean up |

**[PL]**: 6 stale branches remain. These were identified in v3 meeting but not yet cleaned. Assign to [CODE] for next session.

---

## 10. Code Review (This Session)

**[CV]**: See `code_review_2026_02_19_v1.md` for full review.

Summary:
- Phase 17-A commits reviewed: ✅ All APPROVED
- BUG-114 filed: Mobile card click timeout (E2E test infrastructure issue)
- Outstanding code quality items (carried from Phase 17-E):
  - `market_data_service.py` L755 redundant `SAVE_INTERVAL` — still open
  - Debug prints — still open
  - Bare `except` clauses — still open

---

## 11. Product Document Review

**[PM]**: Quick audit of `docs/product/`:

| Document | Status | Action |
|----------|--------|--------|
| `tasks.md` | ✅ Current | Phase 17-A progress reflected |
| `correlation_report_full.csv` | ✅ New | Saved to `docs/product/` |
| `duckdb_architecture.md` | ⚠️ Stale | Post-Phase 16 changes not reflected |
| `data_pipeline.md` | ⚠️ Stale | Should reference MI_INDEX + Goodinfo + KY sources |
| `mars_strategy_bcr.md` | ⚠️ Needs update | Should reflect 71.2%/82.1% match rate |

**[PL]**: Document refresh is Phase 17-E housekeeping. Non-blocking.

---

## 12. Mobile Web Layout Review

**[UI]**: No frontend changes since last session. Open mobile bugs:
- **BUG-114-CV**: Mobile card click timeout (new) — Playwright test infrastructure issue
- **BUG-113-CV**: Mobile card expand z-index issue
- **BUG-112-CV**: Transaction modal confirm timeout
- **BUG-008**: Mobile login overlay viewport clipping

All 4 are Phase 8 items. Mobile layout is functional but not premium-refined.

**[UI]**: Root cause for BUG-113/BUG-114 is likely the same: the `TSMC` div is in the DOM but hidden at mobile breakpoint. The desktop table row is hidden, but the mobile card's visible element uses a different selector. Fix: add `data-testid="mobile-stock-card"` for reliable targeting.

---

## 13. Brainstorming Review (Product Status)

**[PM]**: Multi-agent brainstorming lens:

### ✅ Strengths
- **Data accuracy**: 71.2%/82.1% match rate — massive improvement from 62.9%/78.8%
- **Root causes identified**: OTC gap + split cap are the remaining 3% gap
- **Architecture**: DuckDB single source of truth, MarketCache in-memory, all commits pushed

### ⚠️ Risks
- **Zeabur still stale**: Remote has Phase 17-A code but not the DuckDB data
- **No Parquet backup**: `market.duckdb` is still a single point of failure
- **Stale branches**: 6 branches not yet cleaned up

### 🔮 Opportunities
- **Phase 17-B**: Boss can verify all tabs locally now — data is clean
- **OTC crawler**: Would push match rate to ~84%+ (within 1% of target)
- **Large split cap**: Quick fix, ~1% improvement

---

## 14. Integration with tasks.md

**[PL]**: `tasks.md` needs update to reflect Phase 17-A progress:
- Mark `Fix TWT49U 権息 parser` as ✅ done
- Mark `Re-run Grand Correlation v5` as 🟡 in progress (v6 at 71.2%/82.1%)
- Add BUG-114 to bug tracking

---

## 15. Decisions & Action Items

| # | Decision / Action | Owner | Priority | Deadline |
|---|-------------------|-------|----------|----------|
| 1 | **Add `data/raw_dividends/*.json` to `.gitignore`** | [CODE] | 🔴 High | Next session |
| 2 | **Commit BUG-114 Jira ticket + analysis CSVs** | [CODE] | 🔴 High | Next session |
| 3 | **Cap stock dividend value in `generate_ky_patches.py`** (≤20.0) | [CODE] | 🟡 Medium | Next session |
| 4 | **Clean up 6 stale branches** | [PL]/[CODE] | 🟡 Medium | This week |
| 5 | **Move debug scripts** to `tests/ops_scripts/` | [CODE] | 🔵 Low | This week |
| 6 | **Local web app verification** (Phase 17-B) | BOSS | 🟡 When ready | — |
| 7 | **Zeabur Deployment** (Phase 17-C) | [CODE]/[SPEC] | ⬜ After 17-B | — |
| 8 | **Update `tasks.md`** (Phase 17-A progress) | [PL] | 🔵 Low | This session |
| 9 | **Address BUG-113/114 mobile card visibility** | [UI] | 🔵 Low | Phase 8 |

---

## [PL] Summary Report to Terran

Boss, here's where we stand at 00:46 HKT (2026-02-19):

**Phase 17-A Grand Correlation**: v6 at **71.2% (±1.5%) / 82.1% (±3.0%)**. All commits pushed to `origin/master`. The remaining ~3% gap is fully understood:
1. **OTC history gap** (~2%): Stocks that transferred from TPEx→TWSE (e.g., 6472 Bora) — needs a new OTC crawler
2. **Large split ratio distortion** (~1%): KY stocks with par-value changes — fixable with a cap (≤20.0) in `generate_ky_patches.py`

**New bug filed**: BUG-114-CV — Mobile portfolio card click timeout in E2E tests. Same root cause as BUG-113 (mobile card visibility). Phase 8 item, non-blocking.

**Immediate next steps**:
1. 🔴 Add `data/raw_dividends/*.json` to `.gitignore` + commit cleanup
2. 🟡 Cap large split ratios in `generate_ky_patches.py` → re-run Grand Correlation v7
3. 🟡 **Phase 17-B**: You verify Mars, BCR, Compound Interest, Cash Ladder tabs locally
4. ⬜ Phase 17-C: Zeabur Deployment (after 17-B)

No blockers for Phase 17-B. Data is clean. App is running. Ready for your verification whenever you are.

---

**Reported by**: [PL]
**Next Meeting**: After Phase 17-B local verification + Phase 17-C Zeabur deployment.
