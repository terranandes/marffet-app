# Agents Sync Meeting Notes

**Date:** 2026-01-17 13:00 UTC+8  
**Attendees:** [PM], [SPEC], [PL], [CODE], [UI], [CV]  
**Location:** `/meeting/`

---

## [PL] Meeting Agenda & Summary

### 1. Project Progress ✅

| Phase | Status | Notes |
|-------|--------|-------|
| UI Alignment | ✅ Complete | Legacy + New frontend aligned |
| Pre-warm Automation | ✅ Complete | Rebuild + Push in single commit |
| Cold Run Optimization | ✅ Complete | ~2 min (down from 6+ min) |
| Feature Migration | ✅ 95% Done | Minor UX items remaining |

**Commits Pushed Today:**
- `55d9cf2` - feat: Add System Operations to Legacy UI Admin tab
- `eaa0191` - perf: TPEx batch 10→50, remove dup sleep; feat: Mars auto-warm
- `b286488` - perf: Disable expensive split detection deep scan
- `71211b2` - fix: timedelta import bug in crawler.py
- `679864d` - feat: Manual Pre-warm button now does Rebuild + Push

---

### 2. Current Bugs 🐛

| ID | Description | Severity | Status | Owner |
|----|-------------|----------|--------|-------|
| BUG-001 | Zeabur deployment 404/wrong app | 🔴 High | **NEW** | [PL] |
| BUG-002 | Favicon 404 on legacy UI | 🟢 Low | Known | [UI] |

**[CV] Bug Triage:**
- BUG-001: Zeabur `martian-web.zeabur.app` returns 404, `martian.zeabur.app` shows n8n instead of Martian. Need to check Zeabur dashboard.
- BUG-002: Cosmetic only, defer.

---

### 3. Performance Improvements 🚀

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Cold Run Time | 6+ min | ~2 min | **3x faster** |
| Smart Run (Cache Hit) | N/A | ~27 sec | Cache enabled |
| TPEx Dividend Fetch | Slow | Faster | Batch 50, sleep 0.3s |

**[CODE] Notes:**
- Disabled `detect_daily_split` deep scan (was making 12 API calls/stock/year)
- TPEx batch increased from 10 to 50
- Removed duplicate `asyncio.sleep(0.5)` call

---

### 4. Features Implemented ✅

| Feature | Owner | Status |
|---------|-------|--------|
| Mars Strategy Auto-warm | [CODE] | ✅ Done |
| Rebuild & Push Pre-warm | [CODE] | ✅ Done |
| Single Commit Pre-warm | [CODE] | ✅ Done |
| System Operations in Legacy UI | [UI] | ✅ Done |
| Feature Parity Audit | [CV] | ✅ Done |

---

### 5. Features Unimplemented/Deferred 📋

| Feature | Priority | Reason |
|---------|----------|--------|
| Notifications Bell | Medium | UX enhancement |
| Settings Modal | Low | UX enhancement |
| Language Toggle (i18n) | Low | Not critical |
| Premium Badge | Low | Cosmetic |

---

### 6. Features Planned for Next Phase 🔮

| Feature | Owner | Target |
|---------|-------|--------|
| Full i18n support | [UI] | Phase 3 |
| Mobile app integration | [PM] | Phase 4 |
| Real-time stock alerts | [CODE] | Phase 3 |

---

### 7. Deployment Status 🚀

| Environment | URL | Status |
|-------------|-----|--------|
| Local Backend | http://localhost:8000 | ✅ Running |
| Local Frontend | http://localhost:3000 | ✅ Running |
| Zeabur Backend | martian.zeabur.app | ⚠️ Wrong App |
| Zeabur Frontend | martian-web.zeabur.app | ❌ 404 |

**[PL] Action Required:**
- Check Zeabur dashboard for deployment issues
- Verify environment variables are set
- Redeploy if necessary

---

### 8. Local vs Deployment Discrepancy

| Aspect | Local | Zeabur | Notes |
|--------|-------|--------|-------|
| Mars Page | ✅ Works | ❓ Unknown | Can't test - 404 |
| Race Page | ✅ Works | ❓ Unknown | Can't test - 404 |
| Admin Page | ✅ Works | ❓ Unknown | Can't test - 404 |

---

### 9. User Feedback Process

1. User submits via "Feedback" button
2. Stored in `portfolio.db` → `feedback_reports` table
3. GM Dashboard shows feedback list
4. Status workflow: New → Reviewing → Confirmed → Fixed/Won't Fix
5. AI Agent notes can be added

**No new user feedback today.**

---

### 10. Product Documents Update

| Document | Owner | Updated |
|----------|-------|---------|
| `./product/software_stack.md` | [PL][CODE][UI] | ✅ Current |
| `./product/specifications.md` | [SPEC] | ✅ Current |
| `./product/readme.md` | [PM] | ✅ Current |

---

## [PL] Action Items

1. ⚠️ **HIGH:** Fix Zeabur deployment (404 issue)
2. 📝 Update `software_stack.md` with System Operations alignment
3. 🧪 Re-run Zeabur tests after deployment fix

---

## How to Run the APP

### Local Development

```bash
# Terminal 1: Backend (FastAPI)
cd /home/terwu01/github/martian
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend (Next.js)
cd /home/terwu01/github/martian/frontend
npm run dev

# Access:
# - New Frontend: http://localhost:3000
# - Legacy UI: http://localhost:8000
```

### Production (Zeabur)
- ⚠️ Currently down - needs investigation in Zeabur dashboard

---

**Meeting Adjourned: 13:00 UTC+8**
