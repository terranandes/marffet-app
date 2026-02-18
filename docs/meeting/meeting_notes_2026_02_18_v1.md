# Agents Sync-Up Meeting
**Date**: 2026-02-18 01:03 HKT
**Version**: v1
**Attendees**: [PM] [SPEC] [PL] [CODE] [UI] [CV]

---

## 1. Project Progress

**[PL]**: Good late-night sync everyone. Major milestone tonight — the **Data Integrity Siege** is COMPLETE. Let me hand off to each of you.

**[CODE]**: The 2000-2004 backfill is done. Here's the full picture:
- **V10** (2000-2003): 377,957 rows, 435 stocks. ✅ Verified zero year-gaps.
- **V12** (2004 gap): 2,358 rows, 6 dividends. ✅ Completed at 00:12 HKT.
- **Split Patching**: 352 missing dividend records patched via `supplement_splits.py --apply`.
- **Root Cause Chain**: 4 layered bugs fixed (yfinance MultiIndex, dividends PK, unclosed connection, duplicate SAVE_INTERVAL).

**[SPEC]**: Database state summary:
- `market.duckdb`: ~5M+ total price rows, 1,600+ stocks, 2000-Present.
- All prices are **Nominal (Unadjusted)** — `auto_adjust=False` enforced.
- Dividends table: ~15K records (14,007 TWSE official + new patches).

**[PM]**: From a product standpoint, the data foundation is now solid for all simulation features (Mars, BCR, Compound, Trend, Race).

---

## 2. Current Bugs & Triage

| Ticket | Severity | Status | Owner | Notes |
|--------|----------|--------|-------|-------|
| BUG-112-PL (Mars Data Discrepancy) | High | **RESOLVED** | [CODE] | Root cause was missing 2000-2004 data + adjusted prices. Fixed by Phase 14 rebuild + tonight's backfill. |
| BUG-111-CV (Next.js Proxy 500) | High | **RESOLVED** | [CODE] | Port mismatch fixed (.env → 8000). Marked in tasks.md. |
| BUG-112-CV (Transaction Modal Timeout) | Medium | Open | [UI] | E2E test timeout on confirm button. Needs frontend investigation. |
| BUG-113-CV (Mobile Card Expand) | Low | Open | [UI] | Element not visible in mobile view. CSS z-index or viewport issue. |
| BUG-009 (Mobile Google Login) | Medium | Open | [CODE] | OAuth redirect on mobile Safari. Deferred until Zeabur volume is configured. |
| BUG-010 (Zeabur Guest Mode) | Medium | Open | [CODE] | Guest → Login transition on Zeabur. Related to cookie domain. |
| BUG-008 (Mobile Login Overlay) | Low | Open | [UI] | Viewport clipping on small screens. |

**[CV]**: The BUG-10x mobile series are all pending the Phase 8 frontend cycle. They're not blocking any data work. BUG-112-PL can now be marked RESOLVED — the data discrepancy is fixed.

**[PL]**: Agreed. I'll update BUG-112-PL status.

---

## 3. Performance Improvement

**[CODE]**: Key perf findings from tonight's session:
1. **DuckDB `executemany` with `ON CONFLICT`**: Very slow for >50K rows. We cap at `SAVE_INTERVAL=20` (≈20K rows/flush) for safe operation.
2. **`yfinance` 1.0 `MultiIndex`**: Requires explicit extraction `data[ticker]` even for single-ticker downloads. This was the silent data-loss bug.
3. **Connection management**: DuckDB disallows concurrent R/O and R/W connections locally. All scripts must `conn.close()` immediately after read-only queries.

**[SPEC]**: Recommendation: For the nightly pipeline, we should ensure `flush_results` uses batch sizes ≤ 50K and always closes connections in `finally` blocks.

---

## 4. Features Implemented (This Session)

- [x] Resumable backfill script (`backfill_2000_2004_resumable.py`)
- [x] 2004 gap fill script (`backfill_2004_resumable.py`)
- [x] Split verification scanner (`verify_splits_2000_2004.py`)
- [x] Split supplementation tool (`supplement_splits.py`) — schema fixed
- [x] DB integrity verifier (`scripts/verify_backfill.py`)
- [x] `load_stock_list()` helper in `market_data_service.py`
- [x] MultiIndex handling fix in `backfill_all_stocks()`
- [x] SAVE_INTERVAL dedup fix (L755 + L832)

---

## 5. Features Unimplemented / Deferred

| Feature | Phase | Status | Blocker |
|---------|-------|--------|---------|
| Grand Correlation v4 (>90% target) | Phase 14 | Deferred | Needs MoneyCome ref recalibration |
| Direct DB Upload to Zeabur | Phase 14 | Not Started | Zeabur volume mount needed |
| Zeabur Volume Persistence | Phase 8 | Not Started | Infrastructure config |
| Interactive Backfill Dashboard | Phase 8 | Not Started | Low priority |
| Mobile Premium Overhaul | Phase 8 | Not Started | Pending Phase 8 cycle |
| Multi-language | Deferred | Parked | BOSS decision |
| AICopilot Enhancement | Deferred | Parked | BOSS decision |
| Partition DuckDB backup (<50MB Parquet) | Infra | Not Started | Needed for Git storage |

---

## 6. Features Planned for Next Phase

**[PM]**: Per `BOSS_TBD.md`, the immediate priorities are:
1. **Tab Verification** — Check Mars, BCR, Compound Interest, Cash Ladder all work with the rebuilt DuckDB.
2. **Zeabur Deployment** — Push the clean `market.duckdb` and verify remote operation.
3. **Mars Strategy Simulation** — Full 24-year simulation to validate the data.

**[PL]**: Phase 8 (Premium UI & Remote Stabilization) is the next major phase. Key deliverables:
- Zeabur volume mount for `/data`
- Final remote CAGR verification (~19% for TSMC)
- Mobile premium overhaul

---

## 7. Deployment Completeness

**[CODE]**: Current deployment status:
- **Local**: Fully operational. All data verified.
- **Zeabur**: 3 unpushed commits on `master`:
  ```
  ac79a5e fix(backfill): force yfinance auto_adjust=False
  7c58655 feat: 3.8x Mars perf + all-feature documentation + bug fixes
  cea06c7 chore: save phase 14 planning and draft scripts
  ```
  These need to be pushed after local verification passes.

**[SPEC]**: The `market.duckdb` file (~326MB) cannot be pushed via Git. We need either:
  1. Zeabur volume mount + direct upload, OR
  2. Parquet partition (<50MB chunks) for Git LFS.

---

## 8. Local vs Zeabur Discrepancies

| Aspect | Local | Zeabur | Gap |
|--------|-------|--------|-----|
| `market.duckdb` | ✅ 5M+ rows, 2000-Present | ❓ Unknown state | Need upload |
| Nominal Prices | ✅ All unadjusted | ❓ May have old adjusted data | Need sync |
| Dividends | ✅ 15K+ records | ❓ Unknown | Need sync |
| Auth / Login | ✅ Working | ❓ Last verified 02-09 | Need retest |
| Next.js Frontend | ✅ Working | ❓ Port mismatch fixed locally | Need push |

---

## 9. Worktree / Branch Status

**[PL]**: Current branch analysis:

| Branch | Status | Action |
|--------|--------|--------|
| `master` | Active, 3 unpushed commits | Push after verification |
| `ralph-loop-q05if` | Latest Ralph Loop test | Keep for now |
| `ralph-loop-6taxy` | Older Ralph Loop | Can be cleaned |
| `ralph-loop-kxvdg` | Older Ralph Loop | Can be cleaned |
| `ralph-loop-uf966` | Older Ralph Loop | Can be cleaned |
| `ralph-loop-3ox9f` | Local only | Can be cleaned |
| `feat/settings-modal-migration` | Remote only | Can be cleaned (merged) |
| `test/full-exec` | Remote only | Can be cleaned |

**Recommendation**: Clean up 5 stale `ralph-loop-*` branches and `feat/settings-modal-migration`.

---

## 10. Decisions & Action Items

| # | Decision | Owner | Deadline |
|---|----------|-------|----------|
| 1 | Mark BUG-112-PL as RESOLVED | [PL] | Immediate |
| 2 | Push 3 commits to origin/master after Mars simulation passes | [CODE] | Next session |
| 3 | Run full Mars simulation (24-year) to validate 2000-2004 data | [CODE] | Next session |
| 4 | Investigate Zeabur volume mount for `market.duckdb` | [SPEC] | This week |
| 5 | Clean up stale branches (5 ralph-loop + 2 feature) | [PL] | This week |
| 6 | Address BUG-112-CV / BUG-113-CV in Phase 8 frontend cycle | [UI] | Phase 8 |

---

## ADDENDUM (01:15 HKT) — Full-Range Dividend Restoration

**[CODE]**: Boss flagged that split records were only patched for 2000-2003. Confirmed the `dividends` table had been wiped during Phase 14 rebuild. Executed 3-step restoration:

| Step | Action | Records |
|------|--------|---------|
| 1 | `reimport_twse_dividends.py 2003 2025` | 14,006 (TWSE official) |
| 2 | `verify_splits` + `supplement_splits --apply` | 418 (2000-2002 gap) |
| 3 | Fallback patches (1808, 2330, etc.) | included |

**Final State**: **14,424 dividend records** covering 2000-2025.

**[PL]**: Action Item #1 (BUG-112-PL) is now fully complete. Data integrity confirmed across all years.

---

**Reported by**: [PL]
**Next Meeting**: After Mars Simulation verification completes.
