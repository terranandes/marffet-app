# Meeting Notes: Agents Sync-Up

**Date:** 2026-02-07 17:55:00
**Version:** v5
**Participants:** [PL], [PM], [SPEC], [UI], [CODE], [CV]

## 1. Project Status Overview
- **[PL]**: We've successfully addressed the key user feedback regarding the **Compound Interest Page**. The native implementation is now much more robust and accurate.
- **[PM]**: Correlation with **MoneyCome.in** is the current gold standard. The recent fixes have aligned our numbers with theirs, which builds significant trust.

## 2. Recent Accomplishments (Compound Page Refinement)
- **API Connectivity**: Fixed the Zeabur deployment issue by switching to relative API URLs (`/api/...` instead of `API_BASE`).
- **Total Investment Calculation**:
    - **[UI]**: Fixed the display to include the contribution on the start year.
    - Formula: `Principal + ((EndYear - StartYear + 1) * Contribution)`
    - Verified: 2006-2007 with 1M + 60K/yr = **$1,120,000 matches MoneyCome**.
- **Formula Hints & Rules**:
    - **[SPEC]**: Added detailed MoneyCome rules to both the skeleton and results sections.
    - **[CODE]**: Confirmed backend logic (`calculator.py`) correctly handles dividend reinvestment:
        1. Cash dividends based on *held shares*.
        2. Reinvested at *yearly average price*.
    - **[UI]**: Hints are now visible in both Empty State and Result State.

## 3. Pending/deferred Items
- **Comparison Mode Verification**:
    - **[CV]**: We verified Single Mode. Next step is to strictly verify **Comparison Mode** logic against MoneyCome's "Buy At Opening" strategy for multiple stocks.
- **Mobile Layout**:
    - **[UI]**: The new formula hints might take up space on mobile. Need to verify responsiveness.

## 4. Product Documentation Updates
- **[SPEC]**: Updated `product/specifications.md` to v3.1, adding **Section 6: Compound Interest Logic**.
- **[PL]**: Updated `product/tasks.md`, marking Compound Interest and Comparison tabs as **Native Implementation** (removed "Iframe Wrapper" status).

## 5. Next Steps
- **[PL]**: Proceed to `full-test` workflow to ensure no regressions.
- **[CV]**: Create a codified test case for the "Total Investment" formula to prevent future regressions.

## 6. Action Items
1.  **[CV]** Add automated test for Compound Interest calculation logic (Total Inv mismatch prevention).
2.  **[UI]** Double-check mobile view for the new hints.
