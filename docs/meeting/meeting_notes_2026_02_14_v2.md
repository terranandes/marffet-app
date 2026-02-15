# Meeting Notes - 2026-02-14 (v2) - Nominal Reset Sync

**Objective**: Align on Phase 14 "Nominal Price Standardization" to fix Grand Correlation discrepancies.

## 👥 Attendees
- [PL] Project Leader
- [PM] Product Manager
- [SPEC] Spec Manager
- [CODE] Backend Builder
- [UI] Frontend Designer
- [CV] Code Verification

## 📑 Agenda & Discussion

### 1. Progress & Bottlenecks
- **Progress**: Phase 13 successfully identified 'Double Adjustment' as the root cause for 82% of CAGR discrepancies. Dividend database is now 100% nominal and verified.
- **Gaps**: DuckDB currently contains backward-adjusted prices for many stocks.

### 2. Triage & Decisions
- **Decision: Nominal Reset**: The team voted unanimously to PERMANENTLY standardize DuckDB on a Nominal Price basis. 
- **Decision: MI_INDEX Mass Fetch**: Adopt daily MI_INDEX checkpointing as the primary price restoration source (4,800 requests vs 460,000 requests).
- **Decision: DB Direct Sync**: Once local validation passes >90%, the local `market.duckdb` will be uploaded directly to Zeabur to avoid cloud-side rate limit failures.

### 3. Roles & Assignments
- **[PM]**: Updated `moneycome_methodology.md` and `specifications.md` to mandate a 100% Nominal Basis.
- **[CODE]**: Implementing the `fetch_mi_index_mass.py` script with adaptive WAF backoff.
- **[CV]**: Creating a 'Basis Audit' gate to prevent future TRI contamination.
- **[UI]**: Planning an 'Integrity Status' indicator for the Admin dashboard.

## 🏁 Actions for Phase 14
1. [ ] Implement MI_INDEX Mass Fetcher.
2. [ ] Rebuild DuckDB `daily_prices` from pure nominal data.
3. [ ] Run Grand Correlation v4.
4. [ ] Direct DB Sync to Zeabur.

**Next Meeting**: 2026-02-15 or upon Phase 14 completion.
