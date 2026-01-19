# Agents Sync-Up Meeting Notes
**Date:** 2026-01-19
**Version:** v1
**Participants:** [PM], [PL], [SPEC], [UI], [CODE], [CV]

---

## 1. Project Progress & Features Implemented

**[PL]**: Welcome everyone. Today's focus is the major stability fixes we've deployed to Zeabur. We've had a very productive session resolving critical login/logout issues.

**[CODE]**: I can confirm that the **Login/Logout Flow** is now fully functional for all user types (Guest, Regular, GM/Admin). We identified three critical bugs that were causing issues:
1.  **Backend Session Clearing**: Switched from `session.pop()` to `session.clear()` to ensure cross-origin cookies are properly updated.
2.  **CORS Configuration**: Removed a duplicate middleware that was blocking credentials.
3.  **Frontend State Management**: Fixed a bug where `setUser({id: null})` was causing the UI to think a user was still logged in.

**[UI]**: On the frontend side, we also fixed the **UI Flicker (FOUC)**. The login buttons used to flash briefly before the user profile loaded. I've implemented a proper `isLoading` state with a skeleton loader, so the transition is now smooth.

**[PM]**: Excellent work. Stability is key for user trust. What about the missing stock name issue?

**[CODE]**: That's resolved too. Stock 6533 (Andes Technology) was missing from our offline Excel database, so it was falling back to English names from YFinance. We've added a **Supplementary Name Cache** to manually map it to "晶心科技". We also have a plan to implement a robust API-based fetcher from TWSE/TPEx for future cases.

## 2. Current Bugs & Triages

**[PL]**: We have one new bug reported by the User (Terran) regarding the Default Portfolio.

**[CV] (Bug Report)**:
- **Issue**: When a user deletes *all* targets in their portfolio groups, the "Default Portfolio" (Mars/Bond/ETF) reappears.
- **Expected Behavior**: The Default Portfolio should *only* appear for a **new user's first login**. If an existing user clears their portfolio, it should stay empty.
- **Root Cause (Hypothesis)**: The `list_groups()` function likely checks `if not groups:` and auto-initializes defaults, without distinguishing between "new user" and "user who deleted everything".

**[SPEC]**: We need to define "New User" more strictly. Perhaps check a `is_initialized` flag in the user profile or `user_groups` table, rather than just checking if the group list is empty.

**[CODE]**: Agreed. I'll modify the logic to check if the user has *ever* had groups, or add a flag.

## 3. Discrepancy between Local-Run and Deployment

**[PL]**: How are we looking on Zeabur vs Local?

**[CV]**:
- **Login/Logout**: Matches. Both working correctly now.
- **Stock Names**: Matches. 6533 fix is deployed.
- **Performance**: Zeabur is stable. Cold run optimization is working well.
- **Health Check**: `/health` endpoint is active and useful for monitoring.

## 4. Product File Updates

**[SPEC]**: I will update `product/test_plan.md` to include the new regression tests for Login/Logout and the Stock Name verification.

**[PM]**: `product/README.md` and `datasheet.md` look good for now, but we should add a section about the "Default Portfolio" behavior once fixed, so users know it's a starter template they can remove.

## 5. Next Steps

**[PL]**: Here is the plan:
1.  **[CODE]** Fix the "Default Portfolio" bug (priority).
2.  **[CODE]** Implement the formal TWSE/TPEx API fetcher for Chinese names (to replace/augment manual patching).
3.  **[CV]** Verify the fixes on Zeabur.
4.  **[PL]** Final report to Terran.

---

**[PL]**: Meeting adjourned. Let's get that portfolio bug fixed!
