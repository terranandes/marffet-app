# Agents Sync Meeting - 2026-02-08
**Attendees:** [PM] [SPEC] [PL] [CODE] [UI] [CV]
**Time:** 04:18 (Local)

---

## 1. Project Progress Summary

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 2: UNADJUSTED Prices | ✅ Complete | TWSE/TPEx direct API (2010+) |
| Phase 3: Mars Correlation | ✅ Complete | Split detection, CAGR verified |
| Phase 4.1: Endpoint Optimization | ✅ Complete | `MarketCache` integrated |
| Phase 4: Universal Data Lake | 🔄 Deferred | Daily OHLCV (Parquet) deferred |
| Frontend Refactor | ✅ Complete | 900 lines → components/hooks |
| Data Verification | 🔄 In Progress | ROI correlation 22% match |

---

## 2. Jira Triage

### Critical (P0)
| ID | Title | Status | Owner |
|----|-------|--------|-------|
| BUG-012 | Zeabur Backend 502 | **OPEN** | [PL]/Terran |

### High (P1)
| ID | Title | Status | Owner |
|----|-------|--------|-------|
| BUG-011 | Transaction Edit Broken | OPEN | [CODE] |
| BUG-010 | Zeabur Guest Mode Login | OPEN | [CODE] |

### Medium (P2)
| ID | Title | Status |
|----|-------|--------|
| BUG-009 | Mobile Google Login | OPEN |
| BUG-008 | Mobile Login Overlay Viewport | OPEN |
| BUG-007 | Transaction Modal Timeout | CLOSED |

### Low (P3)
| ID | Title | Status |
|----|-------|--------|
| BUG-001-006 | E2E Flakiness / Settings Selector | CLOSED |
| BUG-101-104 | CV Test Automation | Addressed |

---

## 3. Performance Improvements

- **[CODE]:** `MarketCache` singleton eliminates redundant API calls. Startup preload ensures 0-latency for all tabs.
- **[SPEC]:** Nested Schema (V2) deployed. Daily data supported.
- **[CV]:** Verified local performance. No OOM on localhost.

---

## 4. Feature Status

### Implemented
- [x] Compound Interest (Native Engine)
- [x] Cash Ladder (Leaderboard)
- [x] Trend (In-Memory Calc)
- [x] Mars Strategy (Correlation)
- [x] Mobile Portfolio Card View

### Deferred
- [ ] Multi-language support
- [ ] AI Copilot enhancements
- [ ] Google Cloud Run migration
- [ ] Daily OHLCV Parquet/DuckDB

---

## 5. Deployment Status

| Environment | Frontend | Backend |
|-------------|----------|---------|
| **Local** | ✅ OK | ✅ OK |
| **Zeabur** | ✅ 200 | ❌ 502 |

**[PL] Action:** Terran needs to check Zeabur Dashboard for container logs/restart.

---

## 6. Local vs Deployment Discrepancy

- **BUG-012:** Backend 502 on Zeabur. Local works perfectly.
- **Root Cause Hypothesis:** OOM on Zeabur free tier OR missing env vars.
- **Mitigation:** Implement "Lite Mode" for `MarketCache` (lazy loading).

---

## 7. Git Worktree Status

| Path | Branch | Action |
|------|--------|--------|
| `/home/terwu01/github/martian` | master | Active |
| `/home/terwu01/github/martian-test-tree` | test-run-master | **Can Clean** |
| `.worktrees/full_test` | master | Active |
| `.worktrees/full_test_20260207` | full-test-20260207 | **Can Clean** |

**[PL] Recommendation:** Clean up `test-run-master` and `full-test-20260207` worktrees.

---

## 8. Next Phase Plan

1. **[CV]:** Re-run ROI verification after cache regeneration (unadjusted data expected to improve match rate).
2. **[PL]:** Push `dae14c4` to master after Zeabur fix.
3. **[CODE]:** Investigate BUG-011 (Transaction Edit).
4. **[UI]:** Review mobile layout for elegance/feasibility.
5. **Terran:** Verify Compound Interest & Cash Ladder tabs per BOSS_TBD.

---

## 9. End-User Feedback Process

1. User reports issue via Settings Modal → Feedback Tab.
2. [CV] triages and files Jira ticket if valid.
3. [PL] assigns priority and owner.
4. Weekly sync reviews all open tickets.

---

## Meeting Adjourned
**Next Meeting:** TBD by Terran.
