# BUG-012: Zeabur Backend 502 - Mars Strategy Shows Zero Results
**Reporter:** [CV] Agent
**Date:** 2026-02-07
**Severity:** **Critical (P0)**
**Environment:** Zeabur Production

## Symptoms
- Mars Strategy page shows "Total Listed: 0, Top Candidates: 0"
- Table displays "Showing top 0 of 0 filtered results"

## Root Cause
Backend API returning HTTP 502 (Bad Gateway):
```bash
$ curl -s -o /dev/null -w "%{http_code}" https://martian-api.zeabur.app/health
502

$ curl -s https://martian-api.zeabur.app/api/results
Bad Gateway
```

## Verification
| Component | URL | Status |
|-----------|-----|--------|
| Frontend (Next.js) | martian-app.zeabur.app | ✅ 200 |
| Backend (FastAPI) | martian-api.zeabur.app | ❌ 502 |

## Likely Causes
1. **Container Crash:** Backend crashed on startup (OOM, missing env var, or Python exception)
2. **Deployment Failure:** Recent push triggered rebuild but container failed to start
3. **Resource Exhaustion:** Zeabur free tier memory limits exceeded

## Resolution Steps
1. **Check Zeabur Dashboard:** View backend container logs for crash reason
2. **Restart Container:** Trigger manual restart via Zeabur UI or redeploy
3. **Verify Env Vars:** Ensure `FRONTEND_URL`, `SECRET_KEY`, `GOOGLE_CLIENT_ID` are set
4. **Check requirements.txt:** Ensure no missing dependencies

## Local Verification
Local environment works correctly:
- `./start_app.sh` runs successfully
- Integration tests: 15/15 PASSED
- E2E tests: All PASSED

**This is a deployment-specific issue, not a code bug.**

**Assigned:** [PL] / Terran (Requires Zeabur Dashboard Access)
