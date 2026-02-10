# Ultra-Fast Crawler Full Integration PRD

> **For Ralph Loop:** This PRD is formatted for autonomous iteration. Each task is self-contained.

## Overview
Integrate the Ultra-Fast Crawler (`crawl_fast.py`) as the **single source of truth** for market data across all tabs, queries, and features.

## Problem
Current state has fragmented data sources:
- `MarketCache` reads from `data/raw/Market_{Year}_Prices.json`
- `fetch_live_prices()` hits yfinance API directly
- `race_cache` SQLite for Race Bar Chart
- Admin tab lacks refresh/backup operations

## Goal
Unified data flow: **Crawler → JSON Files → MarketCache → All Features**

## Prerequisites
- [x] Ultra-Fast Crawler completed (`crawl_fast.py`)
- [ ] Full crawl executed (2000-2026) without rate limit block
- [ ] Data verification passed (`verify_crawl_fast.py`)

---

## Task 1: Update MarketCache to Load Crawler Output

**Files:**
- Modify: `app/services/market_cache.py`

**Acceptance:**
- `MarketCache.get_prices_db()` loads from `data/raw/Market_{Year}_Prices.json` (already done ✅)
- Support V2 schema with `daily` array
- Handle missing years gracefully (2026+ as current year)

**Status:** ✅ Already Implemented

---

## Task 2: Add Admin Tab Refresh Endpoint

**Files:**
- Modify: `app/main.py` (or `app/routers/admin.py` if exists)

**Acceptance:**
- `POST /api/admin/refresh-market-data` endpoint
- Triggers: `MarketCache.get_prices_db(force_reload=True)`
- Auth: Admin-only (owner role)
- Returns: `{ "status": "ok", "years_loaded": 27 }`

**Implementation:**
```python
@router.post("/admin/refresh-market-data")
async def refresh_market_data(user: dict = Depends(get_current_user)):
    if user.get('role') != 'owner':
        raise HTTPException(status_code=403)
    from app.services.market_cache import MarketCache
    db = MarketCache.get_prices_db(force_reload=True)
    return {"status": "ok", "years_loaded": len(db)}
```

---

## Task 3: Add Admin Tab Backup Endpoint

**Files:**
- Modify: `app/main.py`
- Use: `app/services/backup.py`

**Acceptance:**
- `POST /api/admin/backup-market-data` endpoint
- Creates timestamped backup of JSON files
- Returns backup metadata

---

## Task 4: Wire Portfolio Tab to fetch_live_prices()

**Files:**
- Review: `app/services/portfolio_service.py`
- Review: `app/routers/portfolio.py`

**Acceptance:**
- Current value display uses `fetch_live_prices()`
- Historical P&L uses `MarketCache`

**Status:** ✅ Already Implemented (Hybrid Strategy)

---

## Task 5: Wire Analysis Tab to MarketCache

**Files:**
- Review: `app/main.py` (analysis endpoints)

**Acceptance:**
- `/api/mars-strategy` uses `MarketCache.get_prices_db()`
- No direct file reads per request

---

## Task 6: Wire Race Bar Chart to MarketCache

**Files:**
- Modify: `app/services/calculation_service.py`

**Acceptance:**
- Replace `race_cache` SQLite reads with `MarketCache`
- Or keep SQLite as derived cache, populated from `MarketCache`

---

## Task 7: Add Nightly Cron for Current Year Refresh

**Files:**
- New: `scripts/cron/refresh_current_year.sh`
- Use: `tests/ops_scripts/run_crawler_prod.sh`

**Acceptance:**
- Runs at 22:00 HKT daily
- Crawls current year only (2026)
- Triggers webhook to `/api/admin/refresh-market-data`

---

## Task 8: Frontend Integration (All Tabs)

**Files:**
- Review: `frontend/src/services/*`
- Modify: `frontend/src/components/DataTimestamp.tsx` (NEW)

**Acceptance:**
- All data fetches use backend APIs (not direct file reads)
- Portfolio shows live prices with "Live" indicator
- Analysis/History show "Data as of: {date}" timestamp
- First-load shows "Warming up data..." spinner

---

## Task 9: Health Check Endpoint for Cache Status (NEW)

**Files:**
- Modify: `app/main.py`

**Acceptance:**
- `GET /api/health/cache` returns cache status
- Returns: `{ "ready": true, "years": 27, "oldest": "2000", "newest": "2026" }`
- Used by frontend to show loading state

**Implementation:**
```python
@router.get("/health/cache")
async def health_cache():
    from app.services.market_cache import MarketCache, _PRICES_CACHE
    if not _PRICES_CACHE:
        return {"ready": False}
    return {"ready": True, "years": len(_PRICES_CACHE)}
```

---

## Multi-Agent Review Decision Log

| Agent | Objection | Decision | Rationale |
|-------|-----------|----------|-----------|
| Skeptic | No fallback for missing data | ACCEPT | Add graceful degradation |
| Skeptic | Lazy load timeout risk | REJECT | 10s within 30s timeout |
| Skeptic | No rate limiting on admin | DEFER | Low risk for MVP |
| Constraint | Add cache health check | ACCEPT | Task 9 added |
| Constraint | Add cron monitoring | DEFER | Use Zeabur built-in |
| User Advocate | Add freshness indicators | ACCEPT | Task 8 updated |
| User Advocate | Handle first-load gracefully | ACCEPT | Task 8 updated |

**Final Disposition: APPROVED**

---

## Verification Plan

### Automated Tests
```bash
# Unit test for MarketCache reload
uv run pytest tests/unit/test_market_cache.py -v

# Integration test for Admin endpoints
uv run pytest tests/integration/test_admin_refresh.py -v
```

### Manual Verification
1. Deploy to Zeabur staging
2. Trigger `/api/admin/refresh-market-data`
3. Verify all tabs load data correctly

---

## Success Metrics
- **Startup Time**: < 10 seconds (lazy load)
- **Data Freshness**: Portfolio live, others T-1
- **Admin Operations**: Refresh + Backup functional
- **Coverage**: All 9 tasks completed
