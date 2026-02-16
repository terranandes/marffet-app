# Meeting Notes - 2026-02-16 - Phase 14 Execution & Bug Triage

**Objective**: synchronizing on Phase 14 "Nominal Price Standardization" execution and prioritizing critical bug fixes.

## 👥 Attendees
- [PL] Project Leader
- [PM] Product Manager
- [SPEC] Spec Manager
- [CODE] Backend Builder
- [UI] Frontend Designer
- [CV] Code Verification

## 📑 Agenda & Discussion

### 1. Project Status
- **Phase 7 (DuckDB)**: **CLOSED**. The migration is complete and stable.
- **Phase 14 (Nominal Database)**: **IN EXECUTION**.
    - [PM]: "The 'Approved with Revisions' plan is our bible now. We need that 20-year nominal data to fix the Grand Correlation."
    - [PL]: "We are prioritizing the logic for `fetch_mi_index_mass.py` to handle the 2011 schema drift as noted in the plan review."

### 2. Bug Triage
- **BUG-112 (Mars Data Discrepancy)**:
    - **Status**: **Mitigated Locally**.
    - **Analysis**: The local JSON patch proved that missing data was the root cause of the bad CAGR/Wealth metrics.
    - **Resolution**: Phase 14 (Rebuild DB from MI_INDEX) is the permanent fix. We will not deploy the JSON patch to Zeabur; we will deploy the new DuckDB instead.
- **BUG-111 (Next.js 500 Errors)**:
    - **Status**: **CRITICAL**.
    - **Analysis**: Frontend API proxying is failing for specific endpoints (`/auth/me`, `/api/portfolio/*`).
    - **Action**: Check `next.config.ts` rewrites and `frontend/src/app/api` route handlers.
    - **Assignment**: [UI] to investigate immediately. This blocks mobile verification.

### 3. Verification Updates
- [CV]: "I'm preparing the `verify_nominal_integrity.py` suite. It will check:
    1.  No 'adjusted' prices in `daily_prices`.
    2.  Splits are recorded in `stock_actions` but NOT baked into prices.
    3.  Grand Correlation > 90% against MoneyCome."

### 4. Workflow & Housekeeping
- [PL]: "We need to clean up the `ralph-loop` branches after Phase 14 is merged."
- [SPEC]: "Reminding everyone: **Build Local, Deploy Artifact**. Do not try to run the mass fetch on Zeabur."

## 🏁 Actions
1. [ ] **[CODE]** Implement `fetch_mi_index_mass.py` with schema drift handling (Pre-2011 support).
2. [ ] **[CV]** Implement `verify_nominal_integrity.py` .
3. [ ] **[UI]** Fix BUG-111 (Next.js API Proxy).
4. [ ] **[PL]** Merge Phase 14 plan into `tasks.md` (Done).

**Next Meeting**: Post-fix of BUG-111 and initial run of Mass Fetch.
