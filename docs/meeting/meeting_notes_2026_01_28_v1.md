# Meeting Notes: Agents Sync-Up
**Date:** 2026-01-28 00:36 (v1)
**Topic:** OAuth Cookie Fix & Push to Zeabur

---

## 1. [PM] Project Progress

| Phase | Status |
|-------|--------|
| Auth Stabilization | ✅ Complete (Local) |
| Next.js Migration | ✅ Complete |
| Zeabur Deployment | ⏳ Pending Verify |
| Mobile Optimization | 🔜 Deferred |

**Key Win Today:** Fixed intermittent Google Login failure on localhost.

---

## 2. [SPEC] Technical Changes This Session

### `app/main.py`
- **Cookie SameSite Logic:**
  - Production: `SameSite=none` + `Secure=true` (required by Chrome 80+)
  - Localhost: `SameSite=lax` + `Secure=false` (allows OAuth top-level redirects)
- **Root Cause:** Chrome silently rejects `SameSite=none` without `Secure` attribute.

### `app/auth.py`
- Added traceback logging to OAuth callback for better error diagnostics
- Error details now include exception type: `MismatchingStateError: mismatching_state...`

### `kill_martian.sh`
- Added port 3000 (Next.js) and `next-server` process to cleanup script

---

## 3. [CV] Bug Triage

| Ticket | Status | Notes |
|--------|--------|-------|
| BUG-001 | ✅ Fixed | E2E Add Stock Timeout (historical) |
| BUG-005 | ✅ Fixed | Settings Selector |
| BUG-006 | ⚠️ Monitoring | Test Env Flakiness |
| BUG-007 | ✅ Fixed | Transaction Modal Timeout |
| BUG-008 | ✅ Fixed | Mobile Login Overlay Viewport |
| BUG-009 | 🔄 Ready Deploy | Mobile Google Login (Zeabur) |

### BUG-009 Analysis
- **Issue:** `MismatchingStateError` on localhost due to cookie loss
- **Root Cause:** `SameSite=none` without `Secure` → Chrome rejects cookie silently
- **Fix:** Use `SameSite=lax` for localhost (works for OAuth top-level navigations)
- **Status:** ✅ Fixed locally. Zeabur verification pending after push.

---

## 4. [PL] Git Status

**Modified Files (Pending Commit):**
```
M app/auth.py       # Improved error logging
M app/main.py       # SameSite cookie fix
M kill_martian.sh   # Added port 3000/next-server cleanup
M app/portfolio.db  # Runtime data (won't commit)
```

**Branch:** `master`
**Action:** Push auth fixes to trigger Zeabur redeploy.

---

## 5. [UI] Migration Status

| UI | URL | Status |
|----|-----|--------|
| Legacy | https://martian-api.zeabur.app/ | ✅ Working |
| Next.js | https://martian-app.zeabur.app/ | ⏳ Needs Verify |

- Relative path API calls implemented in `Sidebar.tsx`
- Mobile layout: Deferred to next sprint

---

## 6. [CODE] Deployment Checklist

- [x] Local Login works (Legacy 8000)
- [x] Local Login works (Next.js 3000)  
- [ ] Zeabur Legacy Login (martian-api)
- [ ] Zeabur Next.js Login (martian-app)
- [ ] Mobile Safari Login (iPhone)

---

## 7. Next Steps

1. **[PL]** Commit and push `app/auth.py`, `app/main.py`, `kill_martian.sh`
2. **[CV]** Monitor Zeabur deployment completion
3. **[BOSS]** Verify Zeabur login when available
4. **[CV]** Run Playwright E2E suite after Zeabur is stable

---

## How to Run the App

```bash
# Start both backend (8000) and frontend (3000)
./start_app.sh

# Stop all services
./kill_martian.sh
```

**URLs:**
- Legacy UI: http://localhost:8000/
- Next.js UI: http://localhost:3000/

---

**Reported by:** [PL] Project Leader
