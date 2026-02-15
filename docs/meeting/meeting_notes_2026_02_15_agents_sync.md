# Meeting Notes - 2026-02-15 - Phase 14 Kickoff & Sync

**Objective**: Officially kick off Phase 14 "Nominal Price Standardization" and close out Phase 7.

## 👥 Attendees
- [PL] Project Leader
- [PM] Product Manager
- [SPEC] Spec Manager
- [CODE] Backend Builder
- [UI] Frontend Designer
- [CV] Code Verification

## 📑 Agenda & Discussion

### 1. Project Status
- **Phase 7 (DuckDB Core Migration)**: **COMPLETED**.
    - System is fully running on DuckDB.
    - Ops scripts are revamped.
    - Performance is stable.
- **Phase 14 (Nominal Price Standardization)**: **STARTED**.
    - This is the critical path to fixing the 82% discrepancy in Grand Correlation.

### 2. Deep Dive: Phase 14 Execution
- **[PM]**: "We must have a 100% nominal basis. No more backward-adjusted chaos in our primary DB. The `daily_prices` table must reflect what a trader saw on that day."
- **[CODE]**: "I am ready with `fetch_mi_index_mass.py`. This script will pull reliable nominal data from the TWSE MI_INDEX. It's designed to be robust against WAF."
- **[SPEC]**: "Architecture update: `MarketDataProvider` will need a flag or separate method to distinguish 'Adjusted' (for technical analysis) vs 'Nominal' (for valuation/market cap). For now, the base storage is Nominal."
- **[CV]**: "I will need a new verification suite. `verify_nominal_basis.py`? I need to check against known splits to ensure we aren't mixing data types."
- **[UI]**: "I'll update the Admin Dashboard to show the current 'System Basis'. It should say 'NOMINAL' in green when we are done."

### 3. Decisions & Assignments
- **Decision**: The `market.duckdb` will be rebuilt from scratch (or cleaned) to ensure no legacy adjusted data remains in the `daily_prices` table.
- **Assignment [CODE]**: Execute `fetch_mi_index_mass.py` and monitor for 429 errors.
- **Assignment [CV]**: Create a designated test for Nominal Integrity.
- **Assignment [PL]**: Update `tasks.md` to reflect Phase 14.

## 4. Evening Sync (20:58) - Code Review
- **[CODE]** reported `fetch_mi_index_mass.py` draft is ready.
- **[CV]** Review Findings:
    - **Parsing Fragility**: verify line `int(r[2].replace(',', ''))` handles `--` or empty strings.
    - **Schema Match**: Verify `daily_prices` table schema matches the 8 columns being inserted.
    - **Concurrency**: `ON CONFLICT` clause requires a UNIQUE index on `(stock_id, date)`.
- **Action**: [CODE] to harden the script before Full Run (2004-2025).

## 🏁 Actions
1. [ ] **[CODE]** Harden `fetch_mi_index_mass.py` (Handle `--`, Verify Schema).
2. [ ] **[CODE]** Run Test Batch (e.g., Jan 2024).
3. [ ] **[CV]** Develop `verify_nominal_integrity.py`.
4. [ ] **[PL]** Update `docs/product/tasks.md` with Phase 14 items.
5. [ ] **[ALL]** Verify Grand Correlation > 90% once data is ready.

**Next Meeting**: Upon completion of Mass Fetch Test Batch.
