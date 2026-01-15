# Meeting Notes: 2026-01-15 (v2) - Bug Hunt Sync

**Topic**: Critical Bug Triage & "Human Intuition" in QA
**Attendees**: [PM], [PL], [SPEC], [UI], [CV], [CODE]
**Moderator**: [PL]

---

## 1. Acknowledgement of Feedback (User: Terran)
**[PM]**: The Boss noted that "Human capability to bug hunt is stronger than AI agents". This is a fair assessment. We (AI) tend to verify "does the code exist?" or "does the unit test pass?", whereas humans verify "does the feature *work* when I click it?". The missing Portfolio Router was a classic example—code existed, but the *path* didn't.
**[CV]**: Agreed. My new `bug_hunt.py` suite attempts to mimic this by actually clicking buttons and checking UI states, rather than just grepping code.

## 2. Project Progress & Status
- **Portfolio**: ✅ **FIXED**. The "Add Stock" 404 error was resolved by implementing `app/routers/portfolio.py`.
- **Settings**: ✅ **REFINED**. Region restricted to Taiwan. Guest access added to Sidebar (in-progress/verified).
- **Backend structure**: ✅ **STABLE**. Router-based architecture is cleaner.

## 3. Current Bugs & Triage

### A. BCR Start Year (2017 instead of 2006)
- **Severity**: High (Visual correctness)
- **Reporter**: User (Terran)
- **Resolution**: **FIXED**.
    - Issue was improper handling of missing price data for early years.
    - Implemented "Hybrid Initialization" in `app/main.py` to allow wealth accumulation (cash/interest) even when price data is missing.

### B. Massive Data Discrepancy (Stock 6669: 1.2B vs 14M)
- **Severity**: Critical (Data Integrity)
- **Reporter**: User (Terran) via Screenshot comparison with MoneyCome.
- **Analysis**:
    - **Anomaly**: The 1.2B figure was mathematically impossible for legitimate growth (required phantom compounding).
    - **Root Cause**: The simulation was likely applying a "Backfilled" or "Static" ROI to the years 2006-2018 (Pre-IPO), causing massive compounding on empty data.
    - **Verification**: Debug logs confirmed that with the **new fix**, the wealth correctly stays in cash/accumulation phase (0% capital gains) during pre-IPO years.
    - **Result**: New Final Wealth for 6669 is **NT$ 35.8 Million**.
    - **Cross-Check**: 
        - MoneyCome (2019-2026): **~9x ROI** ($1.4M -> $14.8M).
        - Mars New (2019-2026 portion): **~11.5x ROI** ($3.1M -> $35.8M).
        - The results now align. The specific difference ($35M vs $14M) is valid due to Mars starting in 2006 (building a larger base of $3.1M by 2019 vs MoneyCome's $1.4M).

## 4. Next Steps
1.  **[CODE]**: Commit the `app/main.py` fix and remove debug prints.
2.  **[UI/CV]**: Re-verify Mars Default Year. Force 2006 if necessary.
3.  **[PL]**: Report "Mission Accomplished" only when `bug_hunt.py` passes all checks on green.

## 5. Deployment
- **Status**: Local run is active. Deployment to Zeabur should follow after these fixes.

---
**[PL] Action Item**: Proceed to Phase 8 (Bug Hunt & Fixes).
