# Plan Review: Phase 14 Nominal Correction

**Design under Review**: `docs/plan/2026-02-15-phase14-nominal-correction.md`

## 1. Skeptic / Challenger Review
> "Assume this design fails. Why?"

- **Use of `fetch_mi_index`**: Relying on a single scraper for 20 years of data is risky. TWSE often changes formats (e.g., pre-2011 columns might differ). The script must handle schema drift.
- **Split/Dividend Collision**: What if a stock has a Split AND a Stock Dividend in the same month? The `SplitDetector` might suppress the split if it sees a dividend, or vice versa. The logic needs to be deterministic.
- **Data Gap**: What happens if the `mass_fetch` fails for a few days? Do we define "completeness" criteria?

## 2. Constraint Guardian Review
> "Performance, Scalability, Operations"

- **Zeabur Resource Limits**: Rebuilding the DB on Zeabur (cloud) is a bad idea due to CPU/RAM limits and IP rate limiting by TWSE.
- **Upload Bandwidth**: The final DB will be ~100MB-200MB (compressed). Uploading this to Zeabur via Git LFS or direct volume mount is preferred. The plan implies "Direct Sync" but needs to be explicit: **Build Local -> Push to Remote**. Do not run mass fetch on Zeabur.
- **Disk I/O**: Mass inserts into DuckDB are fast, but `WAL` file growth can be an issue. Ensure `checkpoint` is called frequently.

## 3. User Advocate Review
> "User Experience"

- **Maintenance Time**: The user (Boss) wants "Mars Tab" fixed. How long will this take? The "Mass Fetch" is the bottleneck (likely 6-12 hours with rate limits). We should communicate an ETA.
- **Admin Visibility**: The Admin Dashboard should show "Data Basis: NOMINAL" vs "ADJUSTED" to give confidence the fix is applied.

## 4. Arbiter / Integrator Decision

**Disposition**: **APPROVED with REVISIONS**

**Required Actions:**
1.  **Explicit Deployment Strategy**: The plan must state "Build Locally, Upload `market.duckdb` to Zeabur".
2.  **Schema Drift Handling**: `fetch_mi_index_mass.py` must handle the 2011 schema change (TWSE added columns).
3.  **Collision Logic**: `SplitDetector` must explicitly log when it ignores a potential split due to a known dividend, for audit trails.

**Plan Update**: The Implementation Plan assumes these constraints. Proceed to Execution.
