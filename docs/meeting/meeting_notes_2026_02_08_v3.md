# Agents Sync Meeting Notes
**Date:** 2026-02-08
**Version:** v3

## 1. Project Progress
- **Crawler**: `crawl_official.py` completed successfully (1950/1959 stocks).
    - Data: 2000-2026 unadjusted prices now available in `data/raw/Market_{Year}_Prices.json`.
    - Source: yfinance (prices) + TWSE/TPEx (lists).
- **Backend Refactor**:
    - `MarketCache` updated to support 2000+ start year (was 2010).
    - API endpoints updated to remove 2010 restriction.
- **Frontend**:
    - All 4 pages (`mars`, `race`, `compound`, `viz`) reverted to 2006+ default.
    - 2010 limitation removed.

## 2. Current Bugs
| ID | Priority | Description | Status |
|----|----------|-------------|--------|
| BUG-012 | High | Zeabur Backend 502 (OOM/Crash) | Pending Investigation |

## 3. Deployment Status
- **Zeabur**: Deployment likely unstable due to BUG-012.
- **Local**: Functioning correctly with new cached data.

## 4. Planned Features (Next Phase)
- **Ultra-Fast Crawler**: Design approved. To be implemented via Ralph Loop.
    - Target: <15 min runtime (vs current ~1hr).
    - Architecture: Asyncio + Batch Download.

## 5. Action Items
- [PL] Coordinate Ralph Loop execution for crawl_fast.py.
- [CODE] Investigate Zeabur 502 (BUG-012).
- [UI] Verify frontend with new 2000-2009 data.

## 6. Worktree Status
- `.worktrees/full_test`: Active.
- Main worktree: Active.
