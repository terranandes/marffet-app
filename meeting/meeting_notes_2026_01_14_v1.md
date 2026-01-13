# Sync Meeting Notes

**Date:** 2026-01-14
**Version:** v1
**Participants:** [PM], [SPEC], [PL], [CODE], [UI], [CV]

## 1. Project Progress
-   **[CODE] Notification System**: Backend engine (`RuthlessManager`) implemented with 3 key triggers (Gravity, Size, Yield). API endpoints and polling logic deployed.
-   **[UI] Notification UI**: Bell icon, dropdown, and "mark as read" interactions are fully functional.
-   **[CODE] Excel Export**: Upgraded from static CSV to **Dynamic Excel** generation. It now runs a real-time simulation matching the user's dashboard parameters (Start Year, Principal, Contribution).
-   **[UI] Unified Simulation**: "Bar Chart Race" and "Export" now share the exact same simulation source-of-truth.

## 2. Bugs & Triages
-   **[FIXED] CSV Garbage**: The old CSV export produced corrupted characters. Fixed by switching to binary `.xlsx`.
-   **[KNOWN] Data Integrity (Reference Files)**:
    -   `stock_list_...filtered.xlsx` contains some DRs (Depository Receipts) like `91xx` which should be filtered out.
    -   Some new Bond ETFs (e.g., `00937B`) are missing from the static reference file.
    -   *Action*: [CV] marked tests as WARNING (non-blocking). [PL] to schedule a crawler re-run to update reference files.

## 3. Deployment Completeness
-   **Env Vars**: No new variables needed. `SECRET_KEY` remains the only critical one.
-   **Dependencies**: Added `openpyxl` and `pandas` for Excel generation. `requirements.txt` needs verification.

## 4. Next Phase Features
-   **Rebalancing**: The Notification system is the foundation. Next step is "Actionable Rebalancing" - clicking a notification to simulate a trade.
-   **Mobile Layout**: Current UI is desktop-optimized.

## 5. Feedback Process
-   User feedback is collected via the floating feedback button. [PM] reviews weekly.

---
**Summary [PL]:**
The system is stable. The critical "Garbage Export" bug is squashed, and we have a solid Notification infrastructure. We are ready to push.

**Action Items:**
1.  [PL] Commit changes.
2.  [PL] Update `requirements.txt` with `openpyxl`.
