# Meeting Notes: Agents Sync-Up 2026-01-22 v2

**Date:** 2026-01-22 10:10 AM  
**Attendees:** [PM], [SPEC], [PL], [CODE], [UI], [CV]  
**Status:** In Progress  

---

## 1. Project Progress Summary

### Recent Commits (Last 24h)
| Commit | Author | Description |
|--------|--------|-------------|
| `feecf21` | [CODE] | Enable dividend history fetch from DB for modal display |
| `213a66c` | [CODE] | Simplify Backend Port to 8080 (Hardcoded) |
| `9f47c00` | [CODE] | Bind Backend to PORT env variable |
| `86416d5` | [CODE] | Bind Next.js to PORT env variable for Zeabur |
| `a757dc8` | [UI] | Legacy UI dividend click now uses dedicated function |
| `09b99d4` | [UI] | BUG-005 Settings button accessibility and test selectors |
| `0593ab2` | [UI] | Align Next.js UI with Legacy UI format |

### Features Implemented ✅
- [x] Dividend click functionality in Legacy UI
- [x] Dividend history modal with full data from DB
- [x] Next.js P/L colors aligned with Taiwan standard
- [x] Settings button accessibility (aria-label, data-testid)
- [x] OAuth CSRF fix (middleware reordering)

---

## 2. Current Bugs & Jira Triage

| ID | Title | Status | Owner | Notes |
|----|-------|--------|-------|-------|
| BUG-001 | E2E Add Stock Timeout | ⏸️ DEFERRED | [CV] | Manual works, selector needs update |
| BUG-002 | Stock Name 404 | ✅ RESOLVED | [CODE] | Fixed pyproject.toml packaging |
| BUG-003 | Default Portfolio Reappears | ✅ RESOLVED | [CODE] | Fixed duplicate init calls |
| BUG-004 | Instant Name Display | ✅ RESOLVED | [UI] | Fixed newTargetName handling |
| BUG-005 | Settings Button Selector | ✅ RESOLVED | [UI] | Added aria-label and data-testid |
| BUG-006 | CSRF Warning | ✅ RESOLVED | [CODE] | Reordered middleware |
| BUG-007 | Data Alignment 2026 | ✅ RESOLVED | [CODE] | Updated data files |

### New Bug (Just Fixed)
- **Dividend History Empty in Modal**: The DB path didn't fetch history array. Fixed in `feecf21`. Pending deployment verification.

---

## 3. Deployment Status

### Current State
- **Backend (martian-api)**: Last successful deploy was from yesterday (stale files). Recent commits failed to deploy.
- **Frontend (martian-app)**: Port configuration fixed, but runtime status unknown.

### Recent Deployment Fixes
1. `213a66c`: Hardcoded port 8080 in Dockerfile/Procfile
2. `86416d5`: Fixed Next.js to bind to `0.0.0.0:$PORT`

### Action Required (Terran)
> [!IMPORTANT]
> Please manually trigger "Redeploy with Cache Clear" on Zeabur for both services to pick up the latest fixes.

---

## 4. Migration Status: Legacy → Next.js

| Feature | Legacy | Next.js | Parity |
|---------|--------|---------|--------|
| Portfolio View | ✅ | ✅ | 95% |
| Dividend History Modal | ✅ | ✅ | 100% |
| Add/Edit Transaction | ✅ | ✅ | 100% |
| Mars Strategy | ✅ | 🔄 Planned | 0% |
| Cash Ladder | ✅ | 🔄 Planned | 0% |
| Bar Chart Race | ✅ | 🔄 Planned | 0% |

---

## 5. Features Planned for Next Phase

1. **BCR on CAGR as Premium Feature** - Boss requested alignment between Legacy and Next.js
2. **Mars Strategy Migration** - Move to Next.js
3. **Cash Ladder Migration** - Move to Next.js
4. **Mobile Layout Polish** - Fix overflow on small devices (iPhone SE)

---

## 6. Decisions & Action Items

| # | Decision/Action | Owner | Due |
|---|-----------------|-------|-----|
| 1 | Redeploy Zeabur services | [Terran] | Today |
| 2 | Verify dividend history modal after deploy | [CV] | After deploy |
| 3 | Run full E2E test suite | [CV] | After deploy |
| 4 | Fix BUG-001 selector if time permits | [CV] | P2 |
| 5 | Start BCR premium feature implementation | [UI] | Next sprint |

---

## 💡 How to Run the App

### Production (Deployed)
- **Frontend (Next.js)**: [https://martian-app.zeabur.app](https://martian-app.zeabur.app)
- **Legacy UI (FastAPI Static)**: [https://martian-api.zeabur.app](https://martian-api.zeabur.app)

### Local Development
```bash
# Backend
uv run uvicorn app.main:app --reload --port 8000

# Frontend (Next.js)
cd frontend && npm run dev
```

**Access**: 
- Next.js: http://localhost:3000
- Legacy: http://localhost:8000

---

**Next Meeting:** TBD based on deployment verification results.

---
*[PL] Report Compiled at 2026-01-22 10:11 AM*
