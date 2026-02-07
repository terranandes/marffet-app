# Meeting Notes: 2026-01-24 Sync Up

**Date:** 2026-01-24  
**Attendees:** [PM], [PL], [SPEC], [UI], [CV], [CODE]

## 1. Project Progress
- **Guest Mode**: Implemented and verified. `PortfolioService` now reliably detects Guest vs. User mode using `/api/portfolio/targets` probing.
- **Admin UI**: "User Metrics" section aligned horizontally and styled to match "Subscription Breakdown".
- **E2E Testing**: `tests/e2e_suite.py` updated for Next.js app, handling both Guest and Auth scenarios properly.

## 2. Current Bugs & Fixes
- **Fixed**: `uuid` dependency missing in frontend.
- **Fixed**: Guest Mode zombie state (invalid caching/detection).
- **Fixed**: Ambiguous Playwright selectors in "Create Group" flow.
- **Pending**: Settings modal alignment (Legacy vs Next.js) - Added to BOSS_TBD.

## 3. Deployment & Migration
- **Zeabur**: Ready for deployment. Build scripts updated (`fix(build)` in previous header suggests clean up).
- **Migration**: Next.js is now the primary interface. Legacy UI tests moved to `_legacy.py_old`.

## 4. Future Plans
- **Mobile View**: Optimize portfolio card view for narrow screens (BOSS_TBD).
- **Settings Modal**: Port functionality fully to Next.js (BOSS_TBD).
- **Performance**: Monitor Guest Mode LocalStorage limits.

## 5. Action Items
- **[PL]**: Monitor Zeabur deployment status.
- **[UI]**: Design mobile card view for Portfolio.
- **[CODE]**: Ensure `auth_check` endpoint remains lightweight.
