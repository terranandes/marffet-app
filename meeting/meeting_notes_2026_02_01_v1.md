# Meeting Notes: 2026-02-01 (Sprint Sync)

**Date**: 2026-02-01  
**Time**: 16:15  
**Attendees**: [PL], [PM], [SPEC], [CODE], [UI], [CV]  
**Version**: v1  

---

## 1. Project Progress & Deployments
-   **[PL]**: We successfully completed the **Test Environment Tidy-Up**. The `tests/` directory is now structured (`unit`, `e2e`, `integration`, `debug_tools`, `ops_scripts`).
-   **[CODE]**: The **Admin UX Fix** (preventing premature "Complete" alerts) is deployed to Zeabur. Early feedback suggests the progress bar logic is now robust.
-   **[SPEC]**: `product/test_plan.md` has been updated to reflect the new directory structure. Verified 1:1 mapping with the `full-test` workflow.

## 2. Bug Triage (Critical)
**[CV]** reported 3 new bugs from the recent Full System Verification (`@[/full-test]`).

| ID | Severity | Description | Owner | Output |
|----|----------|-------------|-------|--------|
| **BUG-101** | Medium | **E2E Timeout**: Desktop test times out waiting for transaction verification or API response. Flaky. | [CODE] / [CV] | Needs `wait_for_response` instead of `sleep()`. |
| **BUG-102** | **High** | **Mobile Group Tab Missing**: On iPhone 12 viewport, the "Mobile Test" group tab is not clickable (likely hidden sidebar or overflow). | [UI] | Logic check on Mobile Layout (Drawer vs Tabs). |
| **BUG-103** | Medium | **Unit Test Hang**: `test_cb_api.py` hangs indefinitely. Suspect external calls to TWSE. | [CODE] | **Must Mock** external `CrawlerService` calls. |

**Decision**:
-   **Priority 1**: Fix **BUG-102** (Mobile UI). The mobile experience is core to "Anywhere Access".
-   **Priority 2**: Fix **BUG-103** (Unit Test Hang). Running tests shouldn't require internet or hang CI.
-   **Priority 3**: Optimize **BUG-101** (E2E Flakiness).

## 3. Features & UX Review
-   **[PM]**: The **Mars Strategy** simulation is stable. The focus now shifts to **Mobile Polish**. The logic is there, but if the E2E test couldn't find the group tab, users might struggle too.
-   **[UI]**: I suspect the "Sidebar" is hidden on mobile, and the "Group Tabs" might be collapsing into a dropdown or scrolling off-screen. I will review `frontend/src/app/portfolio/page.tsx` for mobile responsiveness.
-   **[SPEC]**: Confirmed that `product/specifications.md` accurately reflects the v2.3 API output (Flat Race Data). No changes needed there.

## 4. Deployment Status
-   **Local**: Fully functional, but Unit Tests are slow (network dependent).
-   **Zeabur (Remote)**: `debug_admin_ops.py` verified the Admin API is healthy. Frontend is live.
-   **Discrepancy**: Local tests failed E2E, but manual usage seems fine. This suggests the *test script* might be brittle, not necessarily the app logic (except for the Mobile UI bug).

## 5. Action Items
1.  **[UI]**: Investigate Mobile Layout group tab visibility (Fix BUG-102).
2.  **[CODE]**: Mock `CrawlerService` in `test_cb_api.py` (Fix BUG-103).
3.  **[CV]**: Refine `e2e_suite.py` to use explicit waits (Fix BUG-101).
4.  **[PL]**: Schedule next deployment after these 3 fixes.

---

**Signed**,  
*The Martian Agents*
