# Agents Sync Meeting: 2026-01-24 "GM Dashboard Focus"

**Date**: 2026-01-24 21:10 (Taipei Time)  
**Attendees**: [PM], [PL], [SPEC], [UI], [CV], [BACKEND]

## 1. Project Status & GM Dashboard
**[PL]**: Terran wants us to focus on the **GM Dashboard**. Status?
**[BACKEND]**: The Admin API is fully implemented in `app/main.py`:
- `/api/admin/metrics`: Returns system usage stats.
- `/api/admin/crawl`: Triggers background crawler (Normal/Cold Run).
- `/api/admin/backup` & `/api/admin/refresh-prewarm`: Manages data safety.
**[UI]**: The frontend interface at `/admin` connects to these endpoints. It allows GM (Terran) to monitor the system and force updates.
**[CV]**: Security is enforced via `GM_EMAILS` check in `app/auth`. Only authorized emails can access these endpoints.

## 2. Recent Achievements (Restore Memory)
- **Infrastructure**: Fixed Zeabur build (deployment is green) and hardened Backup Scheduler (UTC + Grace Period).
- **AI Copilot**: Fixed backend key handling; Chat is functional.
- **Data Integrity**: Fixed `portfolio_db` column mismatch for dividends.
- **UI**: Added "Taiwan Color Convention" (Red=Up, Green=Down).

## 3. Bug Triage (Jira)
- **BUG-001 (E2E Timeout)**: [CV] working on standardizing cleanup in tests to prevent timeouts.
- **BUG-005 (Settings Selector)**: UI issue with selector z-index? Needs verification.
- **BUG-006 (Test Flakiness)**: Related to async DB access in tests.
- **Action**: [PL] prioritizes checking `BUG-005` for UI smoothness.

## 4. Deployment & Migration
- **Zeabur**: Deployment is healthy. `uv` migration complete.
- **Legacy UI**: Fully migrated to Next.js.
- **Mobile Layout**: Next focus for [UI] is ensuring the Dashboard looks great on mobile.

## 5. Code Review Summary
- `app/main.py` Admin section is clean.
- `RuthlessManager` implementation in `api/notifications` is currently "Lazy Triggered" on read.
- **Action**: Consider moving RuthlessManager to a background job if latency increases.

## 6. Next Actions for Terran (User)
- **Run App**: `./start_app.sh` (Auto-setup with `uv`).
- **Verify Dashboard**: Log in with GM Email -> Go to `/admin`.

**Signed off by**: [PL]
