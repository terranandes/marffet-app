# Agents Sync Meeting Notes

**Date:** 2026-01-18 02:46 UTC+8  
**Attendees:** [PM], [SPEC], [PL], [CODE], [UI], [CV]  
**Version:** v3

---

## [PL] Meeting Summary

### 1. Project Progress 🚀

| Feature | Status | Notes |
|---------|--------|-------|
| **Guest Mode** | ✅ Complete | Added to Frontend Sidebar & Backend API (`/auth/guest`) |
| **System Ops Alignment** | ✅ Complete | Legacy UI now has Crawler/Backup buttons |
| **Pre-warm Automation** | ✅ Complete | Asyncio bug fixed. Full rebuild + push takes ~5-6 min |
| **Dividend Data Fix** | 🔄 In Progress | TWSE Dividend caching implemented (`5bf9945`). Pending verification. |

**Commits Pushed since last meeting:**
- `5bf9945` - fix: Enable TWSE dividend data caching (TWT49U) to storage
- `502f320` - docs: Update cold run time estimates
- `b7870bb` - docs: Update test_plan with accurate pre-warm timing
- `2cf33cd` - fix: Asyncio event loop conflict in pre-warm endpoint

---

### 2. Current Bugs & Triages 🐛

| ID | Description | Severity | Owner | Status |
|----|-------------|----------|-------|--------|
| **BUG-003** | **Missing TWSE Dividend Data** | 🔴 Critical | [CODE] | **Fix Committed**. Needs verification. |
| BUG-001 | Zeabur deployment 404/Incorrect App | 🟡 Medium | [PL] | Needs check after recent pushes |
| BUG-002 | Favicon 404 on legacy | 🟢 Low | [UI] | Defer |

**Triage - BUG-003 (TWSE Dividends):**
- **Cause:** `fetch_ex_rights_history` was parsing TWT49U data but *not* saving it to `data/raw/TWSE_Dividends_{year}.json`.
- **Fix:** Added cache check and save logic to the function.
- **Verification Needed:** Run cold run or specific test to confirm `TWSE_Dividends_*.json` files appear.

---

### 3. Performance Improvement ⚡

| Metric | Previous | Current | Improvement |
|--------|----------|---------|-------------|
| **Smart Update** | N/A | **~9 sec** | 🚀 Extremely Fast |
| **Cold Run** | 6+ min | **~6 min** | Accurate baseline established |
| **Pre-warm** | N/A | **~5-6 min** | Fully automated (Rebuild + Push) |

---

### 4. Deployment Check

| Environment | URL | Status |
|-------------|-----|--------|
| Local Backend | `http://localhost:8000` | ✅ Stable |
| Local Frontend | `http://localhost:3000` | ✅ Stable (Guest Mode working) |
| Zeabur Prod | `martian-app.zeabur.app` | ❓ Pending User Verification |

---

## [PL] Action Items

1.  **[CV/User]** Verify TWSE Dividend Fix:
    -   Run "Rebuild All (Cold Run)" or wait for next scheduled run.
    -   Check if Stocks like 5274 (信驊) or 6238 (勝麗) show dividend bars.
2.  **[PL]** Monitor Zeabur deployment status.

---

## How to Run the APP

### Local Development

**1. Backend (Terminal 1)**
```bash
cd /home/terwu01/github/martian
# Ensure venv is active if needed, or use uv run
uv run uvicorn app.main:app --reload --port 8000
```

**2. Frontend (Terminal 2)**
```bash
cd /home/terwu01/github/martian/frontend
npm run dev
```

**3. Access**
- **New Frontend:** [http://localhost:3000](http://localhost:3000) (Use "Continue as Guest")
- **Legacy UI:** [http://localhost:8000](http://localhost:8000)

**Meeting Adjourned: 02:46 UTC+8**
