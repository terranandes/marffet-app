# Martian Project Sync-Up Meeting
**Date:** 2026-01-06
**Attendees:** [PM], [PL], [SPEC], [UI], [CODE], [CV]
**Version:** v1

## 1. Project Progress
**[PL] (Project Leader):**
Team, we've successfully closed out Phase 2 (Data Ingestion) and most of Phase 3 (Dividend Receipts). The system now supports:
- **Full Dividend History (2006-2025)**: Cash + Stock dividends.
- **Dynamic Simulation**: Verified that "Start Year" correctly filters backend data.
- **UI UX**: New Modal for Dividend details is live and working.

**[PM] (Product Manager):**
The new "Dividend Receipt" transparency is great. Users can trust the numbers now. The "Dynamic Table Header" was a small but critical touch for clarity.
**Status**: On Track for Phase 4 (Social Features).

## 2. Bug Triage & Issues
**[CV] (Code Verification):**
I've flagged a critical console error in the latest deployment (Step 2700 Screenshot):
`[Vue warn]: Property "raceConfig" was accessed during render but is not defined on instance.`
This causes the Vue engine to throw `Uncaught TypeError` during render patches.

**[UI] (Frontend Manager):**
Ah, my bad. When we refactored `main.js` to expose `currentYear`, we might have missed adding `raceConfig` to the `return { ... }` object in `setup()`.
**Action**: I will hotfix `main.js` to export `raceConfig` immediately after this meeting.

**[CODE] (Backend Manager):**
Backend is stable. `get_race_data` response time is acceptable even with the dynamic file loading.
No backend bugs reported.

## 3. Deployment & Performance
**[SPEC] (Architect):**
Infrastructure is holding up. We are serving everything via `uvicorn`.
**Reminder**: Ensure `npm` tools are available in the env if we ever move to a build step, but currently we are using pure ESM Vue (CDN-style), so no build step is blocking us yet.

## 4. Next Steps (Phase 4: Social)
**[PM]**:
We need to pivot to **Social Features**.
1.  **Leaderboard**: Populate with mock/real data.
2.  **Public Profiles**: Read-only view of other users' portfolios.
3.  **Sharing**: Generating the shareable link (Done, but needs testing).

**[PL]**:
Agreed. 
1.  **Priority 1**: Fix the `raceConfig` bug.
2.  **Priority 2**: Begin Leaderboard backend logic.

## 5. Summary
- **Simulation**: Fixed & Verified (Dynamic Start Year).
- **Dividends**: Deployed & Verified (Modal).
- **Critical Bug**: `raceConfig` missing in template scope.
- **Next**: Fix user report -> Social Phase.

---
*Meeting Adjourned.*
