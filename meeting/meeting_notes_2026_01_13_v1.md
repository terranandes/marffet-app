# Agents Sync-Up Meeting - 2026-01-13

**Date:** 2026-01-13 03:05  
**Attendees:** [PM] [PL] [SPEC] [CODE] [UI] [CV]

---

## Project Progress Summary

### Session Accomplishments

| Feature | Status | Commits |
|---------|--------|---------|
| **Leaderboard User Persistence** | ✅ Fixed | `184917e` |
| **Bar Chart Race Rendering** | ✅ Fixed | `97099e3`, `213f93c` |
| **CAGR Sorting (Mars Strategy)** | ✅ Fixed | `a42bad8` |
| **CAGR Data Consistency** | ✅ Fixed | `b556130`, `ccc0b3e` |
| **Backend Single Source of Truth** | ✅ Implemented | `1969179` |
| **Bar Chart Race - Top 50** | ✅ Implemented | `d60adac` |

---

## Bugs Fixed This Session

### 1. Leaderboard `rows_updated=0` Bug
- **[CV]**: User stats weren't persisting because UPDATE found no matching row
- **[CODE]**: Implemented UPSERT pattern - INSERT if UPDATE affects 0 rows
- **Status**: ✅ Resolved

### 2. Bar Chart Race - No Bars Rendering
- **[CV]**: Bars had 0 width because `p.cagr` was hardcoded to 0
- **[CODE]**: Fixed data pipeline to use actual values
- **Status**: ✅ Resolved

### 3. CAGR Sorting Incorrect in Mars Strategy
- **[CV]**: Rank 5 (29.80%) appeared after Rank 4 (29.20%)
- **[CODE]**: Changed sort key from `'cagr'` (string) to `'cagr_pct'` (number)
- **Status**: ✅ Resolved

### 4. Bar Chart Race - Static CAGR Values
- **[PM]**: Race should show dynamic per-year CAGR, not final CAGR
- **[SPEC]**: Backend should be Single Source of Truth
- **[CODE]**: Added `cagr` field to `/api/race-data`, removed frontend calculation
- **Status**: ✅ Resolved

---

## Architecture Decision: Single Source of Truth

**[SPEC]** confirmed the data flow:

```
Backend (/api/race-data) calculates:
  - wealth per year
  - cagr per year (cumulative from start_year)
  - roi per year
        ↓
┌────────────────────────────────────────┐
│ Mars Strategy │ CSV Export │ Bar Race  │
└────────────────────────────────────────┘
        (All use same backend data)
```

No frontend calculation - all data comes pre-calculated from backend.

---

## Features Implemented

1. **Leaderboard UPSERT**: Users appear on Cash Ladder after first sync
2. **Dynamic CAGR Racing**: Stocks rise/fall through rankings each year
3. **Top 50 Winners**: Extended from 25 to 50 for comprehensive view
4. **Per-Year CAGR**: Backend calculates CAGR at each year point

---

## Features Deferred / Planned

1. **Tailwind Production Build**: Currently using CDN (dev warning shows)
2. **Vue Production Build**: Currently using development build
3. **Debug Logs Cleanup**: Remove `[Bar Width Debug]` logs before production

---

## Deployment Status

| Environment | Status | Notes |
|-------------|--------|-------|
| **Zeabur** | ✅ Deployed | Auto-deploys on master push |
| **Local** | ✅ Working | `source .venv/bin/activate && uvicorn app.main:app` |

### Environment Variables Required
- `GM_EMAILS`: Admin access control
- `GEMINI_API_KEY`: AI Copilot feature

### Persistent Storage
- **Zeabur**: `/data/portfolio.db` (persistent volume)
- **Local**: `app/portfolio.db`

---

## How to Run the App

### Local Development
```bash
cd /home/terwu01/github/martian
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Then open: http://localhost:8000

### Production (Zeabur)
- Automatic deployment on `git push origin master`
- URL: https://martian-app.zeabur.app (or configured domain)

---

## Action Items

| Owner | Task | Priority |
|-------|------|----------|
| [CV] | Remove debug console.log statements | Medium |
| [CODE] | Consider Vue/Tailwind production builds | Low |
| [PL] | Monitor Zeabur logs for any issues | Ongoing |

---

## Summary for Boss

**Tonight's session accomplished:**
1. ✅ Fixed leaderboard persistence (you're now #1 JDK GRANDMASTER!)
2. ✅ Fixed Bar Chart Race rendering issues
3. ✅ Implemented Single Source of Truth architecture
4. ✅ Dynamic CAGR racing effect works correctly
5. ✅ Extended to top 50 stocks in race

**All commits pushed to master, Zeabur will auto-deploy.**

Good night, Boss! 🌙
